from odoo import models, fields, api
from datetime import datetime

class SportsAthlete(models.Model):
    _name = 'sports.athlete'
    _description = 'Sports Athlete'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Full Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    address = fields.Text(string='Address')

    # Sports-specific fields for athletes
    
    # Athlete identification
    athlete_id = fields.Char(
        string='Athlete ID', 
        copy=False,
        readonly=True,
        help="Unique athlete identification number"
    )
    national_id = fields.Char(string='National ID')
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age')
    age_computed = fields.Integer(string='Age', compute='_compute_age', store=True)
    age_category = fields.Char(string='Age Category', compute='_compute_age_category', store=True)
    
    # Sports Information
    primary_sport = fields.Selection([
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('athletics', 'Athletics'),
        ('swimming', 'Swimming'),
        ('boxing', 'Boxing'),
        ('tennis', 'Tennis'),
        ('netball', 'Netball'),
        ('cricket', 'Cricket'),
        ('rugby', 'Rugby'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('badminton', 'Badminton'),
        ('other', 'Other')
    ], string='Primary Sport')
    
    secondary_sports = fields.Selection([
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('athletics', 'Athletics'),
        ('swimming', 'Swimming'),
        ('boxing', 'Boxing'),
        ('tennis', 'Tennis'),
        ('netball', 'Netball'),
        ('cricket', 'Cricket'),
        ('rugby', 'Rugby'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('badminton', 'Badminton'),
        ('other', 'Other')
    ], string='Secondary Sport')
    position = fields.Char(string='Position/Specialty')
    playing_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('amateur', 'Amateur'),
        ('semi_professional', 'Semi-Professional'),
        ('professional', 'Professional'),
        ('elite', 'Elite')
    ], string='Playing Level', default='amateur')
    
    # Association and Location (for athletes)
    association_id = fields.Many2one('sports.association', string='Sports Association')
    zone_id = fields.Many2one('sports.zone', string='Zone', related='association_id.zone_id', store=True)
    district = fields.Char(string='District')
    
    # Career Information
    career_start_date = fields.Date(string='Career Start Date')
    years_active = fields.Integer(string='Years Active', compute='_compute_years_active')
    
    # Athlete Status (extends the basic attended field)
    athlete_status = fields.Selection([
        ('active', 'Active'),
        ('injured', 'Injured'),
        ('suspended', 'Suspended'),
        ('retired', 'Retired'),
        ('inactive', 'Inactive')
    ], string='Athlete Status', default='active')
    
    # Event Registration Status (for event participation)
    registration_status = fields.Selection([
        ('eligible', 'Eligible'),
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
        ('withdrawn', 'Withdrawn')
    ], string='Registration Status', default='eligible', 
       help="Status for event participation and registration")
    
    # Athlete availability for events
    available_for_events = fields.Boolean(string='Available for Events', default=True,
                                        help="Whether this athlete is available for event selection")
    
    # Performance and Achievements
    performance_metric_ids = fields.One2many('sports.performance.metric', 'athlete_id', string='Performance Metrics')
    achievement_ids = fields.One2many('sports.achievement', 'athlete_id', string='Achievements')
    
    # Statistics (computed)
    total_achievements = fields.Integer(string='Total Achievements', compute='_compute_athlete_statistics', store=True)
    gold_medals = fields.Integer(string='Gold Medals', compute='_compute_athlete_statistics', store=True)
    silver_medals = fields.Integer(string='Silver Medals', compute='_compute_athlete_statistics', store=True)
    bronze_medals = fields.Integer(string='Bronze Medals', compute='_compute_athlete_statistics', store=True)
    
    # Medical Information (for athletes)
    medical_clearance = fields.Boolean(string='Medical Clearance')
    medical_clearance_date = fields.Date(string='Medical Clearance Date')
    medical_notes = fields.Text(string='Medical Notes')
    
    # Emergency Contact (for athletes)
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    
    # Photo
    photo = fields.Binary(string='Photo')
    
    # Relationships (will be added when event integration is enabled)
    # participant_ids = fields.One2many('event.participant', 'athlete_id', string='Event Participations')

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = datetime.now().date()
                record.age_computed = today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
                # Also update the existing age field for consistency
                record.age = record.age_computed
            else:
                record.age_computed = 0

    @api.depends('age_computed')
    def _compute_age_category(self):
        for record in self:
            age = record.age_computed
            if age <= 12:
                record.age_category = 'Under 12'
            elif age <= 15:
                record.age_category = 'Under 15'
            elif age <= 18:
                record.age_category = 'Under 18'
            elif age <= 21:
                record.age_category = 'Under 21'
            elif age <= 30:
                record.age_category = 'Adult (18-30)'
            elif age <= 40:
                record.age_category = 'Masters (31-40)'
            elif age <= 50:
                record.age_category = 'Masters (41-50)'
            else:
                record.age_category = 'Masters (50+)'

    @api.depends('career_start_date')
    def _compute_years_active(self):
        for record in self:
            if record.career_start_date:
                today = datetime.now().date()
                record.years_active = today.year - record.career_start_date.year
            else:
                record.years_active = 0

    @api.depends('achievement_ids')
    def _compute_athlete_statistics(self):
        for record in self:
            achievements = record.achievement_ids
            record.total_achievements = len(achievements)
            record.gold_medals = len(achievements.filtered(lambda x: x.medal_type == 'gold'))
            record.silver_medals = len(achievements.filtered(lambda x: x.medal_type == 'silver'))
            record.bronze_medals = len(achievements.filtered(lambda x: x.medal_type == 'bronze'))

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        for vals in vals_list:
            # Auto-generate athlete ID
            if not vals.get('athlete_id'):
                sequence = self.env['ir.sequence'].next_by_code('sports.athlete') or '000'
                vals['athlete_id'] = f"ATH{sequence}"
        
        return super().create(vals_list)

    def action_retire_athlete(self):
        """Retire the athlete"""
        self.athlete_status = 'retired'

    def action_suspend_athlete(self):
        """Suspend the athlete"""
        self.athlete_status = 'suspended'

    def action_reactivate_athlete(self):
        """Reactivate the athlete"""
        self.athlete_status = 'active'

    def action_view_achievements(self):
        """View all achievements for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Achievements',
            'res_model': 'sports.achievement',
            'view_mode': 'tree,form,kanban',
            'domain': [('athlete_id', '=', self.id)],
            'context': {'default_athlete_id': self.id},
            'target': 'current',
        }

    def action_view_performance_metrics(self):
        """View all performance metrics for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Performance Metrics',
            'res_model': 'sports.performance.metric',
            'view_mode': 'tree,form,graph',
            'domain': [('athlete_id', '=', self.id)],
            'context': {'default_athlete_id': self.id},
            'target': 'current',
        }

    def action_create_achievement(self):
        """Quick create achievement for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Achievement for {self.name}',
            'res_model': 'sports.achievement',
            'view_mode': 'form',
            'context': {'default_athlete_id': self.id},
            'target': 'new',
        }

    def action_create_performance_metric(self):
        """Quick create performance metric for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Performance Metric for {self.name}',
            'res_model': 'sports.performance.metric',
            'view_mode': 'form',
            'context': {'default_athlete_id': self.id},
            'target': 'new',
        }

    @api.model
    def get_import_templates(self):
        """Provide import template for athlete data"""
        return [{
            'label': 'Import Template for Athletes',
            'template': '/sports_tracking/static/xls/athlete_import_template.xlsx'
        }]

    # def action_view_participations(self):
    #     """View all event participations for this athlete"""
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': f'{self.name} - Event Participations',
    #         'res_model': 'event.participant',
    #         'view_mode': 'tree,form',
    #         'domain': [('athlete_id', '=', self.id)],
    #         'context': {'default_athlete_id': self.id},
    #         'target': 'current',
    #     }

    # def action_view_participations(self):
    #     """View all event participations for this athlete"""
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': f'{self.name} - Event Participations',
    #         'res_model': 'event.participant',
    #         'view_mode': 'tree,form',
    #         'domain': [('athlete_id', '=', self.id)],
    #         'context': {'default_athlete_id': self.id},
    #         'target': 'current',
    #     }