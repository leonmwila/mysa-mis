from odoo import models, fields, api
from datetime import datetime


class Artist(models.Model):
    _name = 'artist.artist'
    _description = 'Artist Registry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char('Full Name', required=True, tracking=True)
    artist_id = fields.Char('Artist ID', required=True, copy=False, readonly=True,
                           default=lambda self: self.env['ir.sequence'].next_by_code('artist.artist'))
    stage_name = fields.Char('Stage/Professional Name', tracking=True)
    date_of_birth = fields.Date('Date of Birth', tracking=True)
    age = fields.Integer('Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', tracking=True)
    
    # Contact Information
    phone = fields.Char('Phone Number', tracking=True)
    email = fields.Char('Email Address', tracking=True)
    address = fields.Text('Address', tracking=True)
    emergency_contact = fields.Char('Emergency Contact', tracking=True)
    emergency_phone = fields.Char('Emergency Phone', tracking=True)
    
    # Artistic Information
    art_category = fields.Selection([
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('mixed_media', 'Mixed Media'),
        ('other', 'Other')
    ], string='Primary Art Category', required=True, tracking=True)
    
    specialization = fields.Many2many('artist.specialization', string='Specializations')
    skill_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional'),
        ('master', 'Master')
    ], string='Skill Level', default='beginner', tracking=True)
    
    years_of_experience = fields.Integer('Years of Experience', tracking=True)
    artistic_style = fields.Text('Artistic Style/Description')
    portfolio_url = fields.Char('Portfolio/Website URL')
    
    # Status and Registration
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('retired', 'Retired')
    ], string='Status', default='active', tracking=True)
    
    active = fields.Boolean('Active', default=True)
    
    registration_date = fields.Date('Registration Date', default=fields.Date.today, tracking=True)
    association_ids = fields.Many2many('artist.association', string='Associations')
    zone_id = fields.Many2one('artist.zone', string='Zone', tracking=True)
    
    # Professional Information
    is_professional = fields.Boolean('Professional Artist', tracking=True)
    mentor_id = fields.Many2one('artist.artist', string='Mentor')
    mentee_ids = fields.One2many('artist.artist', 'mentor_id', string='Mentees')
    education_background = fields.Text('Educational Background')
    certifications = fields.Text('Certifications & Awards')
    
    # Performance and Achievement Tracking
    performance_ids = fields.One2many('artist.performance.metric', 'artist_id', string='Performances')
    achievement_ids = fields.One2many('artist.achievement', 'artist_id', string='Achievements')
    total_performances = fields.Integer('Total Performances', compute='_compute_performance_stats', store=True)
    total_achievements = fields.Integer('Total Achievements', compute='_compute_performance_stats', store=True)
    
    # Financial Information (for grants, payments, etc.)
    bank_account = fields.Char('Bank Account Number')
    bank_name = fields.Char('Bank Name')
    tax_id = fields.Char('Tax ID/TIN')
    
    # Images and Documents
    image = fields.Binary('Photo', attachment=True)
    document_ids = fields.One2many('ir.attachment', 'res_id', 
                                  domain=[('res_model', '=', 'artist.artist')], 
                                  string='Documents')
    
    # Analytics and Stats
    overall_rating = fields.Float('Overall Rating', compute='_compute_overall_rating', store=True)
    last_performance_date = fields.Date('Last Performance', compute='_compute_last_performance', store=True)
    
    # Relations for event participation
    event_participants_ids = fields.Many2many(
        'artist.artist', 
        compute='_compute_event_participants',
        string='Event Participants'
    )

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                record.age = today.year - record.date_of_birth.year - \
                           ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
            else:
                record.age = 0

    @api.depends('performance_ids', 'achievement_ids')
    def _compute_performance_stats(self):
        for record in self:
            record.total_performances = len(record.performance_ids)
            record.total_achievements = len(record.achievement_ids)

    @api.depends('performance_ids.overall_rating')
    def _compute_overall_rating(self):
        for record in self:
            if record.performance_ids:
                ratings = record.performance_ids.mapped('overall_rating')
                valid_ratings = [r for r in ratings if r > 0]
                record.overall_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0.0
            else:
                record.overall_rating = 0.0

    @api.depends('performance_ids.performance_date')
    def _compute_last_performance(self):
        for record in self:
            if record.performance_ids:
                record.last_performance_date = max(record.performance_ids.mapped('performance_date'))
            else:
                record.last_performance_date = False

    def _compute_event_participants(self):
        """Compute method for event participants compatibility"""
        for record in self:
            record.event_participants_ids = [(6, 0, [record.id])]

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'artist_id' not in vals_list or not vals_list['artist_id']:
                vals_list['artist_id'] = self.env['ir.sequence'].next_by_code('artist.artist') or 'ART000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'artist_id' not in vals or not vals['artist_id']:
                    vals['artist_id'] = self.env['ir.sequence'].next_by_code('artist.artist') or 'ART000'
        
        return super(Artist, self).create(vals_list)

    def action_view_performances(self):
        """Action to view artist's performances"""
        return {
            'name': f'Performances - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.performance.metric',
            'view_mode': 'tree,form',
            'domain': [('artist_id', '=', self.id)],
            'context': {'default_artist_id': self.id}
        }

    def action_view_achievements(self):
        """Action to view artist's achievements"""
        return {
            'name': f'Achievements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.achievement',
            'view_mode': 'tree,form',
            'domain': [('artist_id', '=', self.id)],
            'context': {'default_artist_id': self.id}
        }

    @api.model
    def get_import_templates(self):
        """Provide import template for artist data"""
        return [{
            'label': 'Import Template for Artists',
            'template': '/artist_tracking/static/xls/artist_import_template.xlsx'
        }]


class ArtistSpecialization(models.Model):
    _name = 'artist.specialization'
    _description = 'Artist Specializations'
    _rec_name = 'name'

    name = fields.Char('Specialization Name', required=True)
    description = fields.Text('Description')
    art_category = fields.Selection([
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('mixed_media', 'Mixed Media'),
        ('other', 'Other')
    ], string='Art Category')
    
    # Examples of specializations:
    # Dance: Ballet, Contemporary, Hip-hop, Traditional, Jazz, etc.
    # Music: Vocal, Piano, Guitar, Drums, Violin, Composition, etc.
    # Visual Arts: Painting, Sculpture, Photography, Drawing, etc.
    # Theater: Acting, Directing, Playwriting, Set Design, etc.