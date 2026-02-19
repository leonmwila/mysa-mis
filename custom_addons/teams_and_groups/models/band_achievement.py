from odoo import models, fields, api


class ArtistBandAchievement(models.Model):
    _name = 'artist.band.achievement'
    _description = 'Artist Band Achievement and Awards'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'achievement_date desc'

    name = fields.Char(string='Achievement/Award Name', required=True)
    band_id = fields.Many2one('artist.band', string='Band/Group', required=True, ondelete='cascade')
    
    # Event/Program Selection
    event_id = fields.Many2one('event.program', string='Event/Program')
    
    # Achievement Details
    achievement_type = fields.Selection([
        ('award', 'Award/Prize'),
        ('certification', 'Certification'),
        ('recognition', 'Recognition'),
        ('scholarship', 'Scholarship/Grant'),
        ('milestone', 'Personal Milestone'),
        ('competition', 'Competition Win'),
        ('exhibition', 'Exhibition Selection'),
        ('performance', 'Notable Performance'),
        ('collaboration', 'Collaboration'),
        ('education', 'Educational Achievement'),
        ('community', 'Community Impact'),
        ('innovation', 'Innovation/Creation'),
        ('other', 'Other')
    ], string='Achievement Type', required=True)
    
    achievement_category = fields.Selection([
        ('artistic', 'Artistic Excellence'),
        ('technical', 'Technical Skill'),
        ('performance', 'Performance Quality'),
        ('creativity', 'Creativity/Innovation'),
        ('leadership', 'Leadership'),
        ('community_service', 'Community Service'),
        ('education', 'Educational'),
        ('collaboration', 'Collaboration'),
        ('cultural_preservation', 'Cultural Preservation'),
        ('youth_development', 'Youth Development'),
        ('other', 'Other')
    ], string='Achievement Category')
    
    # Achievement Information
    achievement_date = fields.Date(string='Achievement Date', required=True)
    location = fields.Char(string='Location')
    event_competition_name = fields.Char(string='Event/Competition Name')
    
    achievement_level = fields.Selection([
        ('local', 'Local'),
        ('district', 'District'),
        ('provincial', 'Provincial'),
        ('national', 'National'),
        ('regional', 'Regional (SADC/East Africa)'),
        ('continental', 'Continental (Africa)'),
        ('international', 'International'),
        ('world', 'World Championship')
    ], string='Achievement Level', default='local')
    
    # Position/Award Details
    position = fields.Integer(string='Position/Rank')
    award_type = fields.Selection([
        ('first_place', '1st Place'),
        ('second_place', '2nd Place'),
        ('third_place', '3rd Place'),
        ('trophy', 'Trophy'),
        ('medal', 'Medal'),
        ('certificate', 'Certificate'),
        ('plaque', 'Plaque'),
        ('other', 'Other')
    ], string='Award Type')
    
    # Issuing Organization
    issuing_organization = fields.Char(string='Issuing Organization')
    
    # Additional Information
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    
    # Verification
    verified = fields.Boolean(string='Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Datetime(string='Verification Date')
    
    # Member achievements (auto-created)
    member_achievement_ids = fields.One2many(
        'artist.achievement',
        'band_achievement_id',
        string='Member Achievements',
        readonly=True
    )
    member_achievements_created = fields.Boolean(
        string='Member Achievements Created',
        default=False,
        readonly=True
    )
    
    @api.model
    def create(self, vals):
        achievement = super(ArtistBandAchievement, self).create(vals)
        # Automatically create achievements for all band members
        achievement._create_member_achievements()
        return achievement
    
    def write(self, vals):
        result = super(ArtistBandAchievement, self).write(vals)
        # If achievement details changed and member achievements not yet created, create them
        if not self.member_achievements_created and any(key in vals for key in ['achievement_type', 'award_type', 'position', 'achievement_date', 'achievement_level']):
            self._create_member_achievements()
        return result
    
    def _create_member_achievements(self):
        """Create achievements for all band members when band wins"""
        if self.member_achievements_created:
            return
        
        Achievement = self.env['artist.achievement']
        
        for member in self.band_id.member_ids:
            # Check if achievement already exists for this member from this band achievement
            existing = Achievement.search([
                ('artist_id', '=', member.id),
                ('band_achievement_id', '=', self.id)
            ], limit=1)
            
            if not existing:
                achievement_vals = {
                    'name': f"{self.name} - Band Achievement",
                    'artist_id': member.id,
                    'achievement_date': self.achievement_date,
                    'achievement_type': self.achievement_type,
                    'achievement_category': self.achievement_category,
                    'achievement_level': self.achievement_level,
                    'location': self.location,
                    'event_competition_name': self.event_competition_name or self.name,
                    'issuing_organization': self.issuing_organization,
                    'description': f"Band Achievement: {self.name}. Band: {self.band_id.name}",
                    'verified': self.verified,
                    'band_achievement_id': self.id,
                }
                
                Achievement.create(achievement_vals)
        
        self.member_achievements_created = True

