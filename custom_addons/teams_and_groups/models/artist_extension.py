from odoo import models, fields, api


class ArtistExtension(models.Model):
    _inherit = 'artist.artist'
    
    # Band/Group membership
    band_ids = fields.Many2many(
        'artist.band',
        'artist_band_artist_rel',
        'artist_id',
        'band_id',
        string='Bands/Groups',
        help="Bands or groups this artist is part of"
    )
    band_count = fields.Integer(string='Number of Bands/Groups', compute='_compute_band_count')
    is_solo = fields.Boolean(string='Solo Artist', default=True, help="Artist performs individually, not as part of a band/group")
    
    @api.depends('band_ids')
    def _compute_band_count(self):
        for artist in self:
            artist.band_count = len(artist.band_ids)
    
    @api.onchange('band_ids')
    def _onchange_band_ids(self):
        """Update solo status based on band membership"""
        if self.band_ids:
            self.is_solo = False
        else:
            self.is_solo = True

