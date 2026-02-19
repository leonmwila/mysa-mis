from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SportsAchievementExtension(models.Model):
    _inherit = 'sports.achievement'

    athlete_id = fields.Many2one('sports.athlete', string='Athlete', required=False)

    award_scope = fields.Selection(
        [
            ('individual', 'Individual'),
            ('team', 'Team'),
        ],
        string='Award For',
        default='individual',
        required=True,
        tracking=True,
    )
    team_id = fields.Many2one(
        'sports.team',
        string='Team or Group',
        tracking=True,
    )
    source_team_award_id = fields.Many2one(
        'sports.achievement',
        string='Source Team Award',
        readonly=True,
        copy=False,
        ondelete='cascade',
    )
    generated_member_award_ids = fields.One2many(
        'sports.achievement',
        'source_team_award_id',
        string='Generated Member Awards',
        readonly=True,
    )
    
    # Link to team achievement (if this achievement was created from a team achievement)
    team_achievement_id = fields.Many2one(
        'sports.team.achievement',
        string='Source Team Achievement',
        readonly=True,
        help="If this achievement was automatically created from a team achievement"
    )
    is_from_team = fields.Boolean(string='From Team Achievement', compute='_compute_is_from_team', store=True)
    
    @api.depends('team_achievement_id')
    def _compute_is_from_team(self):
        for achievement in self:
            achievement.is_from_team = bool(achievement.team_achievement_id)

    @api.constrains('award_scope', 'athlete_id', 'team_id', 'source_team_award_id')
    def _check_award_scope_participant(self):
        for record in self:
            if record.source_team_award_id:
                continue
            if record.award_scope == 'individual' and not record.athlete_id:
                raise ValidationError('Athlete is required for Individual awards.')
            if record.award_scope == 'team' and not record.team_id:
                raise ValidationError('Team or Group is required for Team awards.')

    @api.onchange('award_scope')
    def _onchange_award_scope(self):
        if self.award_scope == 'individual':
            self.team_id = False
        elif self.award_scope == 'team':
            self.athlete_id = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        team_awards = records.filtered(
            lambda r: r.award_scope == 'team' and r.team_id and not r.source_team_award_id
        )
        team_awards._sync_generated_member_awards()
        return records

    def write(self, vals):
        result = super().write(vals)
        sync_keys = {
            'name',
            'achievement_type',
            'medal_type',
            'position',
            'date',
            'location',
            'competition_name',
            'competition_level',
            'performance_value',
            'performance_unit',
            'record_type',
            'points_awarded',
            'prize_money',
            'verified',
            'description',
            'notes',
            'team_id',
            'award_scope',
        }
        if sync_keys.intersection(vals.keys()):
            team_awards = self.filtered(
                lambda r: r.award_scope == 'team' and r.team_id and not r.source_team_award_id
            )
            team_awards._sync_generated_member_awards()
        return result

    def _get_member_award_vals(self, athlete):
        self.ensure_one()
        return {
            'name': self.name,
            'athlete_id': athlete.id,
            'achievement_type': self.achievement_type,
            'medal_type': self.medal_type,
            'position': self.position,
            'date': self.date,
            'location': self.location,
            'competition_name': self.competition_name,
            'competition_level': self.competition_level,
            'performance_value': self.performance_value,
            'performance_unit': self.performance_unit,
            'record_type': self.record_type,
            'points_awarded': self.points_awarded,
            'prize_money': self.prize_money,
            'verified': self.verified,
            'description': self.description,
            'notes': self.notes,
            'team_id': self.team_id.id,
            'award_scope': 'individual',
            'source_team_award_id': self.id,
        }

    def _sync_generated_member_awards(self):
        for record in self:
            if record.source_team_award_id or record.award_scope != 'team' or not record.team_id:
                continue

            existing_by_athlete = {
                award.athlete_id.id: award
                for award in record.generated_member_award_ids
                if award.athlete_id
            }
            team_members = record.team_id.member_ids
            current_member_ids = set(team_members.ids)

            for member in team_members:
                vals = record._get_member_award_vals(member)
                existing = existing_by_athlete.get(member.id)
                if existing:
                    existing.write(vals)
                else:
                    self.create(vals)

            to_remove = record.generated_member_award_ids.filtered(
                lambda award: award.athlete_id.id not in current_member_ids
            )
            if to_remove:
                to_remove.unlink()


class ArtistAchievementExtension(models.Model):
    _inherit = 'artist.achievement'
    
    # Link to band achievement (if this achievement was created from a band achievement)
    band_achievement_id = fields.Many2one(
        'artist.band.achievement',
        string='Source Band Achievement',
        readonly=True,
        help="If this achievement was automatically created from a band achievement"
    )
    is_from_band = fields.Boolean(string='From Band Achievement', compute='_compute_is_from_band', store=True)
    
    @api.depends('band_achievement_id')
    def _compute_is_from_band(self):
        for achievement in self:
            achievement.is_from_band = bool(achievement.band_achievement_id)

