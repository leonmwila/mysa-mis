from odoo import models, fields, api

class SportsAssociation(models.Model):
    _name = 'sports.association'
    _description = 'Sports Association Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Association Name', required=True)
    short_name = fields.Char(string='Short Name')
    registration_number = fields.Char(string='Registration Number')
    
    # Contact Information
    contact_person = fields.Char(string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Physical Address')
    
    # Location
    zone_id = fields.Many2one('sports.zone', string='Zone', required=True)
    district = fields.Char(string='District')
    
    # Sports Details
    sports_type = fields.Selection([
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
    ], string='Primary Sport', required=True)
    
    secondary_sports = fields.Char(string='Secondary Sports')
    
    # Status and Registration
    status = fields.Selection([
        ('pending', 'Pending Registration'),
        ('registered', 'Registered'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive')
    ], string='Status', default='pending', required=True)
    
    established_date = fields.Date(string='Date Established')
    registration_date = fields.Date(string='Registration Date')
    expiry_date = fields.Date(string='Registration Expiry')
    
    # Statistics
    total_athletes = fields.Integer(string='Total Athletes', compute='_compute_statistics')
    active_athletes = fields.Integer(string='Active Athletes', compute='_compute_statistics')
    total_events = fields.Integer(string='Events Organized', compute='_compute_statistics')
    
    # Relationships
    athlete_ids = fields.One2many('sports.athlete', 'association_id', string='Athletes')
    # event_ids = fields.One2many('event.program', 'organizer_association_id', string='Events Organized')  # Commented out for now since event module is separate
    
    # Additional Information
    description = fields.Text(string='Description')
    logo = fields.Binary(string='Association Logo')
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('athlete_ids')
    def _compute_statistics(self):
        for record in self:
            record.total_athletes = len(record.athlete_ids)
            record.active_athletes = len(record.athlete_ids.filtered(lambda x: x.athlete_status == 'active'))
            record.total_events = 0  # Will be calculated when event integration is added

    def action_register(self):
        """Register the association"""
        self.status = 'registered'
        self.registration_date = fields.Date.today()
        # Set expiry date to 1 year from registration
        from datetime import datetime, timedelta
        if self.registration_date:
            expiry = datetime.strptime(str(self.registration_date), '%Y-%m-%d') + timedelta(days=365)
            self.expiry_date = expiry.date()

    def action_suspend(self):
        """Suspend the association"""
        self.status = 'suspended'

    def action_reactivate(self):
        """Reactivate the association"""
        self.status = 'registered'

    def action_generate_association_report(self):
        """Generate association performance report"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Association Report',
            'res_model': 'sports.analytics',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_association_id': self.id,
                'default_sport_type': self.sports_type,
            }
        }

    def action_view_athletes(self):
        """View all athletes in this association"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Athletes',
            'res_model': 'sports.athlete',
            'view_mode': 'kanban,list,form',
            'domain': [('association_id', '=', self.id)],
            'context': {'default_association_id': self.id}
        }

    def action_view_active_athletes(self):
        """View active athletes in this association"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Active Athletes',
            'res_model': 'sports.athlete',
            'view_mode': 'kanban,list,form',
            'domain': [('association_id', '=', self.id), ('athlete_status', '=', 'active')],
            'context': {'default_association_id': self.id}
        }

    def action_view_events(self):
        """View events organized by this association"""
        # For now, return a simple message since event integration is not active
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Events',
                'message': 'Event management will be available when event integration is enabled.',
                'type': 'info'
            }
        }