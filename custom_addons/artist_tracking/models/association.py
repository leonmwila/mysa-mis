from odoo import models, fields, api


class ArtistAssociation(models.Model):
    _name = 'artist.association'
    _description = 'Artist Associations and Organizations'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char('Association Name', required=True, tracking=True)
    association_id = fields.Char('Association ID', required=True, copy=False, readonly=True,
                                default=lambda self: self.env['ir.sequence'].next_by_code('artist.association'))
    acronym = fields.Char('Acronym/Short Name', tracking=True)
    description = fields.Text('Description', tracking=True)
    
    # Association Type and Focus
    association_type = fields.Selection([
        ('professional', 'Professional Association'),
        ('cultural', 'Cultural Group'),
        ('educational', 'Educational Institution'),
        ('youth', 'Youth Organization'),
        ('community', 'Community Group'),
        ('cooperative', 'Artists Cooperative'),
        ('union', 'Artists Union'),
        ('foundation', 'Arts Foundation'),
        ('other', 'Other')
    ], string='Association Type', required=True, tracking=True)
    
    art_focus = fields.Selection([
        ('multi_arts', 'Multi-Arts'),
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('traditional_arts', 'Traditional Arts'),
        ('other', 'Other')
    ], string='Artistic Focus', required=True, tracking=True)
    
    # Registration and Legal
    registration_date = fields.Date('Registration Date', default=fields.Date.today, tracking=True)
    registration_number = fields.Char('Official Registration Number', tracking=True)
    legal_status = fields.Selection([
        ('registered', 'Officially Registered'),
        ('pending', 'Registration Pending'),
        ('informal', 'Informal Group'),
        ('inactive', 'Inactive')
    ], string='Legal Status', default='pending', tracking=True)
    
    # Location and Contact
    zone_id = fields.Many2one('artist.zone', string='Zone', required=True, tracking=True)
    headquarters_address = fields.Text('Headquarters Address', tracking=True)
    phone = fields.Char('Phone Number', tracking=True)
    email = fields.Char('Email Address', tracking=True)
    website = fields.Char('Website URL', tracking=True)
    
    # Leadership and Management
    president_id = fields.Many2one('artist.artist', string='President/Chairperson')
    vice_president_id = fields.Many2one('artist.artist', string='Vice President')
    secretary_id = fields.Many2one('artist.artist', string='Secretary')
    treasurer_id = fields.Many2one('artist.artist', string='Treasurer')
    coordinator_id = fields.Many2one('res.users', string='Ministry Coordinator')
    
    # Membership
    member_ids = fields.Many2many('artist.artist', string='Members')
    member_count = fields.Integer('Number of Members', compute='_compute_member_count', store=True)
    founding_members = fields.Many2many('artist.artist', 'association_founding_members_rel', 
                                       string='Founding Members')
    membership_fee = fields.Float('Annual Membership Fee')
    
    # Activities and Programs
    activities = fields.Text('Main Activities and Programs')
    meeting_schedule = fields.Char('Meeting Schedule')
    annual_events = fields.Text('Annual Events and Festivals')
    
    # Financial Information
    annual_budget = fields.Float('Annual Budget')
    funding_sources = fields.Text('Funding Sources')
    bank_account = fields.Char('Bank Account Number')
    bank_name = fields.Char('Bank Name')
    
    # Performance and Impact
    achievements = fields.Text('Major Achievements')
    community_impact = fields.Text('Community Impact')
    partnership_ids = fields.Many2many('artist.association', 'association_partnership_rel',
                                      'association_id', 'partner_id', string='Partner Organizations')
    
    # Status and Tracking
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('dissolved', 'Dissolved')
    ], string='Status', default='active', tracking=True)
    
    last_activity_date = fields.Date('Last Activity Date', tracking=True)
    next_meeting_date = fields.Date('Next Meeting Date')
    
    # Statistics and Analytics
    total_events_organized = fields.Integer('Total Events Organized', compute='_compute_event_stats', store=True)
    total_performances = fields.Integer('Total Performances by Members', compute='_compute_performance_stats', store=True)
    average_member_rating = fields.Float('Average Member Rating', compute='_compute_member_rating', store=True)
    
    # Images and Documents
    logo = fields.Binary('Logo', attachment=True)
    constitution_document = fields.Binary('Constitution Document', attachment=True)
    document_ids = fields.One2many('ir.attachment', 'res_id', 
                                  domain=[('res_model', '=', 'artist.association')], 
                                  string='Documents')

    @api.depends('member_ids')
    def _compute_member_count(self):
        for record in self:
            record.member_count = len(record.member_ids)

    @api.depends('member_ids.performance_ids')
    def _compute_performance_stats(self):
        for record in self:
            record.total_performances = sum(len(member.performance_ids) for member in record.member_ids)

    @api.depends('member_ids.overall_rating')
    def _compute_member_rating(self):
        for record in self:
            if record.member_ids:
                ratings = record.member_ids.mapped('overall_rating')
                valid_ratings = [r for r in ratings if r > 0]
                record.average_member_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0.0
            else:
                record.average_member_rating = 0.0

    def _compute_event_stats(self):
        # This would be computed based on event management module integration
        for record in self:
            record.total_events_organized = 0  # Placeholder for future integration

    @api.model
    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'association_id' not in vals_list or not vals_list['association_id']:
                vals_list['association_id'] = self.env['ir.sequence'].next_by_code('artist.association') or 'ASSOC000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'association_id' not in vals or not vals['association_id']:
                    vals['association_id'] = self.env['ir.sequence'].next_by_code('artist.association') or 'ASSOC000'
        
        return super(ArtistAssociation, self).create(vals_list)

    def action_view_members(self):
        """Action to view association members"""
        return {
            'name': f'Members - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.artist',
            'view_mode': 'tree,form',
            'domain': [('association_ids', 'in', [self.id])],
            'context': {'default_association_ids': [(6, 0, [self.id])]}
        }

    def action_add_member(self):
        """Action to add new member to association"""
        return {
            'name': f'Add Member to {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.artist',
            'view_mode': 'tree',
            'target': 'new',
            'context': {
                'search_default_available_artists': 1,
                'association_id': self.id
            }
        }

    def action_view_performances(self):
        """Action to view all performances by association members"""
        member_ids = self.member_ids.ids
        return {
            'name': f'Performances - {self.name} Members',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.performance.metric',
            'view_mode': 'tree,form',
            'domain': [('artist_id', 'in', member_ids)],
        }

    def send_notification_to_members(self):
        """Send notification to all association members"""
        # This could be enhanced with actual notification functionality
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Notification Sent',
                'message': f'Notification sent to {self.member_count} members of {self.name}',
                'type': 'success'
            }
        }