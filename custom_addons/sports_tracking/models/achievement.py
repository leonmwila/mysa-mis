from odoo import models, fields, api

class SportsAchievement(models.Model):
    _name = 'sports.achievement'
    _description = 'Sports Achievement and Awards'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Achievement Title', required=True)
    athlete_id = fields.Many2one('sports.athlete', string='Athlete', required=True)
    
    # Event/Program Selection - will be added by event_program_management module if installed
    # Using manual text field as fallback
    
    # These fields will be auto-populated from the selected event
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
    
    # Event Information
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
        ('international', 'International/World')
    ], string='Competition Level', required=True)
    
    # Performance Details
    performance_value = fields.Float(string='Performance Value')
    performance_unit = fields.Char(string='Unit')
    record_type = fields.Selection([
        ('national', 'National Record'),
        ('regional', 'Regional Record'),
        ('games', 'Games Record'),
        ('meet', 'Meet Record'),
        ('personal', 'Personal Best')
    ], string='Record Type')
    
    # Achievement Value
    points_awarded = fields.Float(string='Points Awarded')
    prize_money = fields.Float(string='Prize Money (ZMW)')
    
    # Verification
    verified = fields.Boolean(string='Verified', default=False)
    verified_by_id = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime(string='Verification Date')
    
    # Documentation
    certificate_image = fields.Binary(string='Certificate/Award Image')
    media_coverage = fields.Text(string='Media Coverage')
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    
    # Related Information
    coach_id = fields.Many2one('res.users', string='Coach')
    team_achievement = fields.Boolean(string='Team Achievement')
    team_members = fields.Char(string='Team Members')

    @api.onchange('achievement_type')
    def _onchange_achievement_type(self):
        if self.achievement_type != 'medal':
            self.medal_type = False
    


    @api.onchange('achievement_type')
    def _onchange_record_type(self):
        if self.achievement_type != 'record':
            self.record_type = False



    def action_verify(self):
        """Verify the achievement"""
        self.verified = True
        self.verified_by_id = self.env.user.id
        self.verification_date = fields.Datetime.now()

    def get_achievement_display_name(self):
        """Get a formatted display name for the achievement"""
        display_parts = []
        
        if self.medal_type:
            display_parts.append(self.medal_type.replace('_', ' ').title())
        
        if self.position and self.achievement_type != 'medal':
            if self.position == 1:
                display_parts.append('1st Place')
            elif self.position == 2:
                display_parts.append('2nd Place')
            elif self.position == 3:
                display_parts.append('3rd Place')
            else:
                display_parts.append(f'{self.position}th Place')
        
        if self.competition_name:
            display_parts.append(f'at {self.competition_name}')
        
        if self.competition_level:
            display_parts.append(f'({self.competition_level.title()} Level)')
        
        return ' '.join(display_parts) if display_parts else self.name

    @api.model
    def get_top_performers(self, sport_type=None, competition_level=None, limit=10):
        """Get top performing participants based on achievements"""
        domain = [('verified', '=', True)]
        
        if sport_type:
            domain.append(('athlete_id.primary_sport', '=', sport_type))
        
        if competition_level:
            domain.append(('competition_level', '=', competition_level))
        
        # Group by participant and count achievements
        achievements = self.search(domain)
        participant_scores = {}
        
        for achievement in achievements:
            athlete = achievement.athlete_id
            if athlete.id not in participant_scores:
                participant_scores[athlete.id] = {
                    'participant': athlete,
                    'total_achievements': 0,
                    'gold_medals': 0,
                    'silver_medals': 0,
                    'bronze_medals': 0,
                    'score': 0
                }
            
            participant_scores[athlete.id]['total_achievements'] += 1
            
            # Calculate score (Gold=3, Silver=2, Bronze=1)
            if achievement.medal_type == 'gold':
                participant_scores[athlete.id]['gold_medals'] += 1
                participant_scores[athlete.id]['score'] += 3
            elif achievement.medal_type == 'silver':
                participant_scores[athlete.id]['silver_medals'] += 1
                participant_scores[athlete.id]['score'] += 2
            elif achievement.medal_type == 'bronze':
                participant_scores[athlete.id]['bronze_medals'] += 1
                participant_scores[athlete.id]['score'] += 1
        
        # Sort by score and return top performers
        top_performers = sorted(participant_scores.values(), 
                              key=lambda x: (x['score'], x['gold_medals'], x['silver_medals']), 
                              reverse=True)
        
        return top_performers[:limit]

    def action_verify(self):
        """Verify the achievement"""
        self.verified = True
        self.verified_by = self.env.user.id
        self.verification_date = fields.Datetime.now()

    def action_view_athlete_achievements(self):
        """View all achievements for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.athlete_id.name} - Achievements',
            'res_model': 'sports.achievement',
            'view_mode': 'kanban,list,form',
            'domain': [('athlete_id', '=', self.athlete_id.id)],
            'context': {'default_athlete_id': self.athlete_id.id}
        }