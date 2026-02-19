from odoo import models, fields, api


class SportsTeamAchievement(models.Model):
    _name = 'sports.team.achievement'
    _description = 'Sports Team Achievement and Awards'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Achievement Title', required=True)
    team_id = fields.Many2one('sports.team', string='Team', required=True, ondelete='cascade')
    
    # Event/Program Selection
    event_id = fields.Many2one('event.program', string='Event/Program')
    
    # Event details (auto-populated from event)
    event_name = fields.Char(string='Event/Competition Name', compute='_compute_event_details', store=True)
    event_date_start = fields.Date(string='Event Start Date', compute='_compute_event_details', store=True)
    event_date_end = fields.Date(string='Event End Date', compute='_compute_event_details', store=True)
    
    # Achievement Details
    achievement_type = fields.Selection([
        ('medal', 'Medal'),
        ('trophy', 'Trophy'),
        ('certificate', 'Certificate'),
        ('record', 'Record'),
        ('award', 'Special Award'),
        ('qualification', 'Qualification'),
        ('other', 'Other')
    ], string='Achievement Type', required=True)
    
    medal_type = fields.Selection([
        ('gold', 'Gold Medal'),
        ('silver', 'Silver Medal'),
        ('bronze', 'Bronze Medal')
    ], string='Medal Type')
    
    position = fields.Integer(string='Position/Rank')
    
    # Achievement Information
    date = fields.Date(string='Achievement Date', required=True)
    location = fields.Char(string='Location')
    competition_name = fields.Char(string='Competition Name')
    
    competition_level = fields.Selection([
        ('local', 'Local'),
        ('district', 'District'),
        ('provincial', 'Provincial'),
        ('national', 'National'),
        ('regional', 'Regional (SADC/East Africa)'),
        ('continental', 'Continental (Africa)'),
        ('international', 'International'),
        ('world', 'World Championship')
    ], string='Competition Level', default='local')
    
    # Additional Information
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    
    # Verification
    verified = fields.Boolean(string='Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Datetime(string='Verification Date')
    
    # Member achievements (auto-created)
    member_achievement_ids = fields.One2many(
        'sports.achievement',
        'team_achievement_id',
        string='Member Achievements',
        readonly=True
    )
    member_achievements_created = fields.Boolean(
        string='Member Achievements Created',
        default=False,
        readonly=True
    )
    
    @api.depends('event_id')
    def _compute_event_details(self):
        for record in self:
            if record.event_id:
                record.event_name = record.event_id.name
                record.event_date_start = record.event_id.start_date
                record.event_date_end = record.event_id.end_date
            else:
                record.event_name = False
                record.event_date_start = False
                record.event_date_end = False
    
    @api.model
    def create(self, vals):
        achievement = super(SportsTeamAchievement, self).create(vals)
        # Automatically create achievements for all team members
        achievement._create_member_achievements()
        return achievement
    
    def write(self, vals):
        result = super(SportsTeamAchievement, self).write(vals)
        # If achievement details changed and member achievements not yet created, create them
        if not self.member_achievements_created and any(key in vals for key in ['achievement_type', 'medal_type', 'position', 'date', 'competition_level']):
            self._create_member_achievements()
        return result
    
    def _create_member_achievements(self):
        """Create achievements for all team members when team wins"""
        if self.member_achievements_created:
            return
        
        Achievement = self.env['sports.achievement']
        
        for member in self.team_id.member_ids:
            # Check if achievement already exists for this member from this team achievement
            existing = Achievement.search([
                ('athlete_id', '=', member.id),
                ('team_achievement_id', '=', self.id)
            ], limit=1)
            
            if not existing:
                achievement_vals = {
                    'name': f"{self.name} - Team Achievement",
                    'athlete_id': member.id,
                    'achievement_type': self.achievement_type,
                    'medal_type': self.medal_type,
                    'position': self.position,
                    'date': self.date,
                    'location': self.location,
                    'competition_name': self.competition_name or self.event_name,
                    'competition_level': self.competition_level,
                    'description': f"Team Achievement: {self.name}. Team: {self.team_id.name}",
                    'verified': self.verified,
                    'team_achievement_id': self.id,
                }
                
                if self.event_id:
                    achievement_vals['event_name'] = self.event_id.name
                    achievement_vals['event_date_start'] = self.event_id.start_date
                    achievement_vals['event_date_end'] = self.event_id.end_date
                
                Achievement.create(achievement_vals)
        
        self.member_achievements_created = True

