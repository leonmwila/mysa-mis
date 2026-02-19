from odoo import models, fields, api
from datetime import datetime


class ArtistBand(models.Model):
    _name = 'artist.band'
    _description = 'Artist Band or Group'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Band/Group Name', required=True, tracking=True)
    band_id = fields.Char(
        string='Band ID',
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('artist.band'),
        help="Unique band/group identification number"
    )
    
    # Art Category
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
    
    # Band Details
    description = fields.Text(string='Description')
    formation_date = fields.Date(string='Formation Date', tracking=True)
    band_type = fields.Selection([
        ('band', 'Music Band'),
        ('group', 'Dance Group'),
        ('ensemble', 'Ensemble'),
        ('troupe', 'Troupe'),
        ('collective', 'Collective'),
        ('other', 'Other')
    ], string='Band/Group Type', default='band', tracking=True)
    
    # Management
    manager_name = fields.Char(string='Manager Name', tracking=True)
    manager_contact = fields.Char(string='Manager Contact')
    leader_id = fields.Many2one('artist.artist', string='Band Leader', tracking=True)
    
    # Location/Zone
    zone_id = fields.Many2one('artist.zone', string='Zone', tracking=True)
    location = fields.Char(string='Location', tracking=True)
    
    # Association
    association_id = fields.Many2one('artist.association', string='Association', tracking=True)
    common_association_id = fields.Many2one('common.association', string='Association/Organization', tracking=True)
    
    # Band Members
    member_ids = fields.Many2many(
        'artist.artist',
        'artist_band_artist_rel',
        'band_id',
        'artist_id',
        string='Band Members',
        tracking=True
    )
    member_count = fields.Integer(string='Number of Members', compute='_compute_member_count', store=True)
    
    # Event Participation
    event_ids = fields.Many2many(
        'event.program',
        'artist_band_event_rel',
        'band_id',
        'event_id',
        string='Events Participated'
    )
    
    # Achievements
    achievement_ids = fields.One2many('artist.band.achievement', 'band_id', string='Band Achievements')
    achievement_count = fields.Integer(string='Achievement Count', compute='_compute_achievement_count')
    
    # Status
    active = fields.Boolean(string='Active', default=True, tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('disbanded', 'Disbanded')
    ], string='Status', default='active', tracking=True)
    
    @api.depends('member_ids')
    def _compute_member_count(self):
        for band in self:
            band.member_count = len(band.member_ids)
    
    @api.depends('achievement_ids')
    def _compute_achievement_count(self):
        for band in self:
            band.achievement_count = len(band.achievement_ids)
    
    def write(self, vals):
        """Override write to sync band members to event artist participants when members change"""
        result = super().write(vals)
        
        # If member_ids changed, update events/programs
        if 'member_ids' in vals:
            for band in self:
                # Find all events/programs this band participates in
                events = self.env['event.program'].search([
                    ('band_participants_ids', 'in', [band.id])
                ])
                for event in events:
                    # Add band members to event artist participants (if field exists)
                    if hasattr(event, 'artist_participants_ids') and band.member_ids:
                        event.artist_participants_ids = event.artist_participants_ids | band.member_ids
        
        return result
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('band_id'):
                vals['band_id'] = self.env['ir.sequence'].next_by_code('artist.band')
        return super(ArtistBand, self).create(vals_list)
    
    def action_view_achievements(self):
        """View band achievements"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Achievements',
            'res_model': 'artist.band.achievement',
            'view_mode': 'tree,form',
            'domain': [('band_id', '=', self.id)],
            'context': {'default_band_id': self.id}
        }
    
    def action_view_members(self):
        """View band members"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Members',
            'res_model': 'artist.artist',
            'view_mode': 'tree,form',
            'domain': [('band_ids', 'in', [self.id])],
        }

