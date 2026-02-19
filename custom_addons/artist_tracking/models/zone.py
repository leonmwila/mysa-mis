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
    artist_selection_ids = fields.Many2many(
        'artist.artist',
        string='Artists',
        compute='_compute_artist_selection_ids',
        inverse='_inverse_artist_selection_ids',
    )
    artist_count = fields.Integer('Number of Artists', compute='_compute_artist_count', store=True)
    common_association_ids = fields.Many2many(
        'common.association',
        'artist_zone_common_association_rel',
        'zone_id',
        'association_id',
        string='Associations/Organizations',
        domain=[('is_arts', '=', True)],
    )
    association_count = fields.Integer('Number of Associations', compute='_compute_association_count', store=True)
    
    # Cultural Centers and Venues
    venue_ids = fields.One2many('artist.venue', 'zone_id', string='Cultural Venues')
    venue_selection_ids = fields.Many2many(
        'artist.venue',
        string='Cultural Venues',
        compute='_compute_venue_selection_ids',
        inverse='_inverse_venue_selection_ids',
    )

    @api.depends('artist_ids')
    def _compute_artist_selection_ids(self):
        for record in self:
            record.artist_selection_ids = record.artist_ids

    def _inverse_artist_selection_ids(self):
        for record in self:
            selected_artists = record.artist_selection_ids
            selected_artists.write({'zone_id': record.id})
            removed_artists = self.env['artist.artist'].search([
                ('zone_id', '=', record.id),
                ('id', 'not in', selected_artists.ids),
            ])
            if removed_artists:
                removed_artists.write({'zone_id': False})

    @api.depends('venue_ids')
    def _compute_venue_selection_ids(self):
        for record in self:
            record.venue_selection_ids = record.venue_ids

    def _inverse_venue_selection_ids(self):
        for record in self:
            selected_venues = record.venue_selection_ids
            selected_venues.write({'zone_id': record.id})
            removed_venues = self.env['artist.venue'].search([
                ('zone_id', '=', record.id),
                ('id', 'not in', selected_venues.ids),
            ])
            if removed_venues:
                removed_venues.write({'zone_id': False})
    
    @api.depends('artist_ids')
    def _compute_artist_count(self):
        for record in self:
            record.artist_count = len(record.artist_ids)

    @api.depends('common_association_ids')
    def _compute_association_count(self):
        for record in self:
            record.association_count = len(record.common_association_ids)

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
            'res_model': 'common.association',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.common_association_ids.ids)],
            'context': {'default_is_arts': True}
        }


class ArtistVenueExtension(models.Model):
    _inherit = 'artist.venue'

    zone_id = fields.Many2one('artist.zone', string='Zone')
    performance_ids = fields.One2many('artist.performance.metric', 'venue_id', string='Performances')
    performance_count = fields.Integer('Number of Performances', compute='_compute_performance_count', store=True)

    @api.depends('performance_ids')
    def _compute_performance_count(self):
        for record in self:
            record.performance_count = len(record.performance_ids)