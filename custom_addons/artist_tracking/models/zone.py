from odoo import models, fields, api


class ArtistZone(models.Model):
    _name = 'artist.zone'
    _description = 'Artist Zones - Geographical Organization'
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char('Zone Name', required=True)
    code = fields.Char('Zone Code', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    
    # Geographical Information
    region = fields.Selection([
        ('national', 'National'),
        ('provincial', 'Provincial'),
        ('district', 'District'),
        ('municipal', 'Municipal'),
        ('community', 'Community')
    ], string='Region Type', default='district')
    
    parent_zone_id = fields.Many2one('artist.zone', string='Parent Zone')
    child_zone_ids = fields.One2many('artist.zone', 'parent_zone_id', string='Sub-Zones')
    
    # Contact Information
    zone_coordinator = fields.Many2one('res.users', string='Zone Coordinator')
    coordinator_phone = fields.Char('Coordinator Phone')
    coordinator_email = fields.Char('Coordinator Email')
    office_address = fields.Text('Office Address')
    
    # Status
    active = fields.Boolean('Active', default=True)
    
    # Statistics
    artist_ids = fields.One2many('artist.artist', 'zone_id', string='Artists')
    artist_count = fields.Integer('Number of Artists', compute='_compute_artist_count', store=True)
    association_ids = fields.One2many('artist.association', 'zone_id', string='Associations')
    association_count = fields.Integer('Number of Associations', compute='_compute_association_count', store=True)
    
    # Cultural Centers and Venues
    venue_ids = fields.One2many('artist.venue', 'zone_id', string='Cultural Venues')
    
    @api.depends('artist_ids')
    def _compute_artist_count(self):
        for record in self:
            record.artist_count = len(record.artist_ids)

    @api.depends('association_ids')
    def _compute_association_count(self):
        for record in self:
            record.association_count = len(record.association_ids)

    def action_view_artists(self):
        """Action to view zone's artists"""
        return {
            'name': f'Artists in {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.artist',
            'view_mode': 'tree,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id}
        }

    def action_view_associations(self):
        """Action to view zone's associations"""
        return {
            'name': f'Associations in {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.association',
            'view_mode': 'tree,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id}
        }


class ArtistVenue(models.Model):
    _name = 'artist.venue'
    _description = 'Cultural Venues and Performance Spaces'
    _rec_name = 'name'

    name = fields.Char('Venue Name', required=True)
    venue_type = fields.Selection([
        ('theater', 'Theater'),
        ('gallery', 'Art Gallery'),
        ('concert_hall', 'Concert Hall'),
        ('studio', 'Studio'),
        ('community_center', 'Community Center'),
        ('outdoor_space', 'Outdoor Space'),
        ('museum', 'Museum'),
        ('cultural_center', 'Cultural Center'),
        ('other', 'Other')
    ], string='Venue Type', required=True)
    
    # Location
    zone_id = fields.Many2one('artist.zone', string='Zone', required=True)
    address = fields.Text('Address')
    capacity = fields.Integer('Capacity')
    
    # Contact and Management
    manager_name = fields.Char('Manager Name')
    manager_phone = fields.Char('Manager Phone')
    manager_email = fields.Char('Manager Email')
    
    # Facilities and Equipment
    facilities = fields.Text('Available Facilities')
    equipment = fields.Text('Available Equipment')
    accessibility = fields.Boolean('Wheelchair Accessible')
    parking_available = fields.Boolean('Parking Available')
    
    # Booking and Availability
    booking_required = fields.Boolean('Booking Required', default=True)
    booking_contact = fields.Char('Booking Contact')
    rental_rate = fields.Float('Rental Rate per Hour')
    
    # Status
    active = fields.Boolean('Active', default=True)
    
    # Statistics
    performance_ids = fields.One2many('artist.performance.metric', 'venue_id', string='Performances')
    performance_count = fields.Integer('Number of Performances', compute='_compute_performance_count', store=True)
    
    @api.depends('performance_ids')
    def _compute_performance_count(self):
        for record in self:
            record.performance_count = len(record.performance_ids)