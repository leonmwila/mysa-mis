from odoo import models, fields, api
from datetime import datetime


class SportsTeam(models.Model):
    _name = 'sports.team'
    _description = 'Sports Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Team Name', required=True, tracking=True)
    team_id = fields.Char(
        string='Team ID',
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sports.team'),
        help="Unique team identification number"
    )
    
    # Sport Information
    sport = fields.Selection([
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
    ], string='Sport', required=True, tracking=True)
    
    # Team Details
    description = fields.Text(string='Description')
    formation_date = fields.Date(string='Formation Date', tracking=True)
    coach_name = fields.Char(string='Coach Name', tracking=True)
    coach_contact = fields.Char(string='Coach Contact')
    manager_name = fields.Char(string='Manager Name', tracking=True)
    manager_contact = fields.Char(string='Manager Contact')
    
    # Location/Zone
    zone_id = fields.Many2one('sports.zone', string='Zone', tracking=True)
    location = fields.Char(string='Location', tracking=True)
    
    # Association
    association_id = fields.Many2one('sports.association', string='Association', tracking=True)
    common_association_id = fields.Many2one('common.association', string='Association/Organization', tracking=True)
    
    # Team Members
    member_ids = fields.Many2many(
        'sports.athlete',
        'sports_team_athlete_rel',
        'team_id',
        'athlete_id',
        string='Team Members',
        tracking=True
    )
    member_count = fields.Integer(string='Number of Members', compute='_compute_member_count', store=True)
    
    # Event Participation
    event_ids = fields.Many2many(
        'event.program',
        'sports_team_event_rel',
        'team_id',
        'event_id',
        string='Events Participated'
    )
    
    # Achievements
    achievement_ids = fields.One2many('sports.team.achievement', 'team_id', string='Team Achievements')
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
        for team in self:
            team.member_count = len(team.member_ids)
    
    def write(self, vals):
        """Override write to sync team members to association athletes and event participants when members change"""
        result = super().write(vals)
        
        # If member_ids changed, update associations and events
        if 'member_ids' in vals:
            for team in self:
                # Find all associations this team belongs to
                associations = self.env['sports.association'].search([
                    ('team_ids', 'in', [team.id])
                ])
                for association in associations:
                    # Add team members to association athletes (union to keep existing)
                    if team.member_ids:
                        association.athlete_ids = association.athlete_ids | team.member_ids
                
                # Find all events/programs this team participates in
                events = self.env['event.program'].search([
                    ('team_participants_ids', 'in', [team.id])
                ])
                for event in events:
                    # Add team members to event athlete participants (union to keep existing)
                    if team.member_ids:
                        event.athlete_participants_ids = event.athlete_participants_ids | team.member_ids

                # Re-sync team-scoped sports achievements to current team members
                team_awards = self.env['sports.achievement'].search([
                    ('team_id', '=', team.id),
                    ('award_scope', '=', 'team'),
                    ('source_team_award_id', '=', False),
                ])
                if team_awards:
                    team_awards._sync_generated_member_awards()
        
        return result
    
    @api.depends('achievement_ids')
    def _compute_achievement_count(self):
        for team in self:
            team.achievement_count = len(team.achievement_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('team_id'):
                vals['team_id'] = self.env['ir.sequence'].next_by_code('sports.team')
        return super(SportsTeam, self).create(vals_list)
    
    def action_view_achievements(self):
        """View team achievements"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Achievements',
            'res_model': 'sports.team.achievement',
            'view_mode': 'tree,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id}
        }
    
    def action_view_members(self):
        """View team members"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Members',
            'res_model': 'sports.athlete',
            'view_mode': 'tree,form',
            'domain': [('team_ids', 'in', [self.id])],
        }

