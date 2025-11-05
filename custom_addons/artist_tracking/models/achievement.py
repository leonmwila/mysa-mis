from odoo import models, fields, api


class ArtistAchievement(models.Model):
    _name = 'artist.achievement'
    _description = 'Artist Achievements and Awards'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'achievement_date desc, id desc'

    # Basic Information
    name = fields.Char('Achievement/Award Name', required=True, tracking=True)
    artist_id = fields.Many2one('artist.artist', string='Artist', required=True, tracking=True)
    achievement_date = fields.Date('Achievement Date', required=True, tracking=True)
    
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
    ], string='Achievement Type', required=True, tracking=True)
    
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
    ], string='Achievement Category', tracking=True)
    
    # Issuing Organization/Event
    issuing_organization = fields.Char('Issuing Organization', tracking=True)
    event_competition_name = fields.Char('Event/Competition Name', tracking=True)
    location = fields.Char('Location', tracking=True)
    
    # Level and Scope
    achievement_level = fields.Selection([
        ('local', 'Local/Community'),
        ('district', 'District'),
        ('provincial', 'Provincial'),
        ('national', 'National'),
        ('regional', 'Regional/Continental'),
        ('international', 'International')
    ], string='Achievement Level', required=True, tracking=True)
    
    competition_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional'),
        ('open', 'Open Category')
    ], string='Competition Level')
    
    # Ranking and Results
    position = fields.Selection([
        ('1st', '1st Place/Gold'),
        ('2nd', '2nd Place/Silver'), 
        ('3rd', '3rd Place/Bronze'),
        ('finalist', 'Finalist'),
        ('semi_finalist', 'Semi-Finalist'),
        ('participant', 'Participant'),
        ('selected', 'Selected/Shortlisted'),
        ('winner', 'Winner'),
        ('runner_up', 'Runner-up'),
        ('special_mention', 'Special Mention'),
        ('other', 'Other')
    ], string='Position/Result', tracking=True)
    
    total_participants = fields.Integer('Total Participants/Applicants')
    score_points = fields.Float('Score/Points Achieved')
    max_score = fields.Float('Maximum Possible Score')
    percentage_score = fields.Float('Percentage Score', compute='_compute_percentage_score', store=True)
    
    # Prize and Recognition
    prize_value = fields.Float('Prize/Award Value')
    monetary_award = fields.Float('Monetary Award')
    scholarship_amount = fields.Float('Scholarship Amount')
    certificate_received = fields.Boolean('Certificate Received', default=True)
    trophy_medal = fields.Boolean('Trophy/Medal Received')
    
    # Art-Specific Details
    artwork_title = fields.Char('Artwork/Performance Title')
    medium_technique = fields.Char('Medium/Technique Used')
    duration = fields.Char('Performance Duration (if applicable)')
    art_category = fields.Selection(related='artist_id.art_category', store=True)
    
    # Criteria and Assessment
    judging_criteria = fields.Text('Judging Criteria')
    judges_panel = fields.Text('Judges/Evaluation Panel')
    evaluation_comments = fields.Text('Evaluation Comments/Feedback')
    
    # Skills and Competencies Demonstrated
    skills_demonstrated = fields.Text('Skills Demonstrated')
    technical_skills = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('satisfactory', 'Satisfactory'),
        ('needs_improvement', 'Needs Improvement')
    ], string='Technical Skills Rating')
    
    creativity_innovation = fields.Selection([
        ('outstanding', 'Outstanding'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('below_average', 'Below Average')
    ], string='Creativity/Innovation Rating')
    
    # Impact and Significance
    personal_significance = fields.Text('Personal Significance')
    career_impact = fields.Text('Career Impact')
    community_impact = fields.Text('Community Impact')
    media_coverage = fields.Boolean('Media Coverage')
    media_links = fields.Text('Media Coverage Links')
    
    # Mentorship and Support
    mentor_support = fields.Boolean('Received Mentor Support')
    mentor_name = fields.Char('Mentor Name')
    institutional_support = fields.Char('Institutional Support Received')
    
    # Follow-up Opportunities
    future_opportunities = fields.Text('Future Opportunities Created')
    networking_contacts = fields.Text('New Professional Contacts')
    collaboration_offers = fields.Text('Collaboration Offers Received')
    
    # Verification and Documentation
    verification_status = fields.Selection([
        ('verified', 'Verified'),
        ('pending', 'Pending Verification'),
        ('unverified', 'Unverified')
    ], string='Verification Status', default='pending', tracking=True)
    
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Date('Verification Date')
    verification_notes = fields.Text('Verification Notes')
    
    # Documentation
    certificate_document = fields.Binary('Certificate/Award Document', attachment=True)
    photo_documentation = fields.Binary('Photo Documentation', attachment=True)
    video_documentation = fields.Binary('Video Documentation', attachment=True)
    press_clippings = fields.Binary('Press Clippings', attachment=True)
    
    # Additional Information
    description = fields.Text('Description', tracking=True)
    preparation_process = fields.Text('Preparation Process')
    challenges_overcome = fields.Text('Challenges Overcome')
    lessons_learned = fields.Text('Lessons Learned')
    acknowledgments = fields.Text('Acknowledgments')
    
    # System Fields
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    public_display = fields.Boolean('Display Publicly', default=True)
    
    # Integration with Event Management (for future integration)
    event_program_id = fields.Many2one('event.program', string='Related Event/Program')

    @api.depends('score_points', 'max_score')
    def _compute_percentage_score(self):
        for record in self:
            if record.max_score and record.max_score > 0:
                record.percentage_score = (record.score_points / record.max_score) * 100
            else:
                record.percentage_score = 0.0

    @api.onchange('artist_id')
    def _onchange_artist_id(self):
        if self.artist_id:
            self.art_category = self.artist_id.art_category

    def action_verify_achievement(self):
        """Verify the achievement"""
        self.write({
            'verification_status': 'verified',
            'verified_by': self.env.user.id,
            'verification_date': fields.Date.today()
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Achievement Verified',
                'message': f'Achievement "{self.name}" has been verified',
                'type': 'success'
            }
        }

    def action_request_verification(self):
        """Request verification for the achievement"""
        # This could be enhanced with actual notification functionality
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Verification Requested',
                'message': f'Verification requested for achievement "{self.name}"',
                'type': 'info'
            }
        }

    def action_share_achievement(self):
        """Share achievement publicly"""
        self.public_display = True
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Achievement Shared',
                'message': f'Achievement "{self.name}" is now publicly visible',
                'type': 'success'
            }
        }


class AchievementCategory(models.Model):
    _name = 'artist.achievement.category'
    _description = 'Achievement Categories'
    _rec_name = 'name'

    name = fields.Char('Category Name', required=True)
    description = fields.Text('Description')
    art_category = fields.Selection([
        ('all', 'All Art Categories'),
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('mixed_media', 'Mixed Media')
    ], string='Applicable Art Category', default='all')
    
    points_value = fields.Integer('Points Value', help='Points awarded for achievements in this category')
    active = fields.Boolean('Active', default=True)


class AchievementLevel(models.Model):
    _name = 'artist.achievement.level'
    _description = 'Achievement Levels'
    _rec_name = 'name'

    name = fields.Char('Level Name', required=True)
    description = fields.Text('Description')
    points_multiplier = fields.Float('Points Multiplier', default=1.0)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)