from odoo import models, fields, api


class SportsAthleteExtension(models.Model):
    _inherit = 'sports.athlete'
    
    # Team membership
    team_ids = fields.Many2many(
        'sports.team',
        'sports_team_athlete_rel',
        'athlete_id',
        'team_id',
        string='Teams',
        help="Teams this athlete is part of"
    )
    team_count = fields.Integer(string='Number of Teams', compute='_compute_team_count')
    is_solo = fields.Boolean(string='Solo Athlete', default=True, help="Athlete participates individually, not as part of a team")
    
    @api.depends('team_ids')
    def _compute_team_count(self):
        for athlete in self:
            athlete.team_count = len(athlete.team_ids)
    
    @api.onchange('team_ids')
    def _onchange_team_ids(self):
        """Update solo status based on team membership"""
        if self.team_ids:
            self.is_solo = False
        else:
            self.is_solo = True

