from odoo import models, fields, api


class SportsAssociationExtension(models.Model):
    _inherit = 'sports.association'

    team_ids = fields.Many2many(
        'sports.team',
        'sports_association_team_rel',
        'association_id',
        'team_id',
        string='Teams'
    )
    band_ids = fields.Many2many(
        'artist.band',
        'sports_association_band_rel',
        'association_id',
        'band_id',
        string='Bands/Groups'
    )
    total_teams = fields.Integer(string='Total Teams', compute='_compute_team_band_statistics')
    total_bands = fields.Integer(string='Total Bands/Groups', compute='_compute_team_band_statistics')

    @api.depends('team_ids', 'band_ids')
    def _compute_team_band_statistics(self):
        for record in self:
            record.total_teams = len(record.team_ids)
            record.total_bands = len(record.band_ids)

    def write(self, vals):
        """Override write to automatically add team members to athletes when teams are added"""
        result = super().write(vals)
        
        # Check if team_ids was modified
        if 'team_ids' in vals:
            for record in self:
                # Get all athletes from all teams in this association
                team_members = self.env['sports.athlete']
                for team in record.team_ids:
                    team_members |= team.member_ids
                
                # Add team members to athlete_ids (union, so existing athletes remain)
                if team_members:
                    record.athlete_ids = record.athlete_ids | team_members
        
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically add team members to athletes"""
        records = super().create(vals_list)
        
        # After creation, sync team members to athletes
        for record in records:
            if record.team_ids:
                team_members = self.env['sports.athlete']
                for team in record.team_ids:
                    team_members |= team.member_ids
                
                if team_members:
                    record.athlete_ids = record.athlete_ids | team_members
        
        return records

    def action_view_teams(self):
        """View all teams in this association"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Teams',
            'res_model': 'sports.team',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.team_ids.ids)],
            'context': {'default_association_id': self.id}
        }

    def action_view_bands(self):
        """View all bands/groups in this association"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Bands/Groups',
            'res_model': 'artist.band',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.band_ids.ids)],
            'context': {'default_association_id': self.id}
        }

