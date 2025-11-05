from odoo import models, fields, api
from datetime import datetime


class ArtistPerformanceMetric(models.Model):
    _name = 'artist.performance.metric'
    _description = 'Artist Performance Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'performance_date desc, id desc'

    # Basic Information
    name = fields.Char('Performance Title', required=True, tracking=True)
    artist_id = fields.Many2one('artist.artist', string='Artist', required=True, tracking=True)
    performance_date = fields.Date('Performance Date', required=True, tracking=True)
    performance_time = fields.Float('Performance Time', help='Time in 24-hour format (e.g., 14.5 for 2:30 PM)')
    
    # Performance Details
    performance_type = fields.Selection([
        ('concert', 'Concert/Recital'),
        ('exhibition', 'Exhibition'),
        ('theater', 'Theater Performance'),
        ('dance', 'Dance Performance'),
        ('workshop', 'Workshop/Masterclass'),
        ('competition', 'Competition'),
        ('festival', 'Festival Performance'),
        ('audition', 'Audition'),
        ('recording', 'Recording Session'),
        ('collaboration', 'Collaboration'),
        ('community', 'Community Event'),
        ('educational', 'Educational Performance'),
        ('other', 'Other')
    ], string='Performance Type', required=True, tracking=True)
    
    art_category = fields.Selection(related='artist_id.art_category', store=True)
    
    # Venue and Location
    venue_id = fields.Many2one('artist.venue', string='Venue')
    venue_name = fields.Char('Venue Name')  # For external venues not in system
    venue_address = fields.Text('Venue Address')
    is_public_performance = fields.Boolean('Public Performance', default=True)
    
    # Audience and Participation
    expected_audience = fields.Integer('Expected Audience Size')
    actual_audience = fields.Integer('Actual Audience Size')
    audience_type = fields.Selection([
        ('general', 'General Public'),
        ('students', 'Students'),
        ('professionals', 'Industry Professionals'),
        ('community', 'Community Members'),
        ('family', 'Family/Friends'),
        ('critics', 'Critics/Media'),
        ('mixed', 'Mixed Audience')
    ], string='Audience Type')
    
    # Performance Quality and Assessment
    self_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Self Rating', tracking=True)
    
    peer_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Peer Rating')
    
    instructor_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Instructor/Director Rating')
    
    audience_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Audience Rating')
    
    overall_rating = fields.Float('Overall Rating', compute='_compute_overall_rating', store=True)
    
    # Technical Aspects (varies by art form)
    technical_skills = fields.Selection([
        ('1', 'Needs Improvement'),
        ('2', 'Developing'),
        ('3', 'Competent'),
        ('4', 'Proficient'),
        ('5', 'Exceptional')
    ], string='Technical Skills')
    
    creativity = fields.Selection([
        ('1', 'Limited'),
        ('2', 'Developing'),
        ('3', 'Good'),
        ('4', 'Strong'),
        ('5', 'Outstanding')
    ], string='Creativity/Innovation')
    
    stage_presence = fields.Selection([
        ('1', 'Needs Work'),
        ('2', 'Developing'),
        ('3', 'Confident'),
        ('4', 'Engaging'),
        ('5', 'Captivating')
    ], string='Stage Presence/Presentation')
    
    # Collaboration and Teamwork (for group performances)
    is_group_performance = fields.Boolean('Group Performance')
    collaborators = fields.Text('Collaborators/Other Artists')
    leadership_role = fields.Boolean('Leadership Role in Performance')
    teamwork_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Teamwork/Collaboration')
    
    # Preparation and Process
    preparation_hours = fields.Float('Preparation Hours')
    rehearsal_sessions = fields.Integer('Number of Rehearsals')
    preparation_quality = fields.Selection([
        ('insufficient', 'Insufficient'),
        ('adequate', 'Adequate'),
        ('good', 'Good'),
        ('thorough', 'Thorough'),
        ('exceptional', 'Exceptional')
    ], string='Preparation Quality')
    
    # Financial Aspects
    performance_fee = fields.Float('Performance Fee Received')
    expenses = fields.Float('Performance Expenses')
    net_income = fields.Float('Net Income', compute='_compute_net_income', store=True)
    
    # Outcomes and Impact
    media_coverage = fields.Boolean('Media Coverage Received')
    media_links = fields.Text('Media Links/Coverage')
    networking_opportunities = fields.Text('Networking Opportunities')
    future_opportunities = fields.Text('Future Opportunities Generated')
    
    # Skills Development
    skills_demonstrated = fields.Text('Skills Demonstrated')
    skills_learned = fields.Text('New Skills Learned')
    areas_for_improvement = fields.Text('Areas for Improvement')
    
    # Additional Information
    description = fields.Text('Performance Description')
    notes = fields.Text('Additional Notes')
    challenges_faced = fields.Text('Challenges Faced')
    lessons_learned = fields.Text('Lessons Learned')
    
    # Status and Documentation
    status = fields.Selection([
        ('planned', 'Planned'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed')
    ], string='Status', default='planned', tracking=True)
    
    # Media and Documentation
    performance_photos = fields.Binary('Performance Photos', attachment=True)
    performance_video = fields.Binary('Performance Video', attachment=True)
    program_document = fields.Binary('Program/Poster', attachment=True)
    
    # System Fields
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date('Approval Date')

    @api.depends('self_rating', 'peer_rating', 'instructor_rating', 'audience_rating')
    def _compute_overall_rating(self):
        for record in self:
            ratings = []
            if record.self_rating:
                ratings.append(float(record.self_rating))
            if record.peer_rating:
                ratings.append(float(record.peer_rating))
            if record.instructor_rating:
                ratings.append(float(record.instructor_rating))
            if record.audience_rating:
                ratings.append(float(record.audience_rating))
            
            record.overall_rating = sum(ratings) / len(ratings) if ratings else 0.0

    @api.depends('performance_fee', 'expenses')
    def _compute_net_income(self):
        for record in self:
            record.net_income = record.performance_fee - record.expenses

    @api.onchange('artist_id')
    def _onchange_artist_id(self):
        if self.artist_id:
            self.art_category = self.artist_id.art_category

    def action_mark_completed(self):
        """Mark performance as completed"""
        self.write({
            'status': 'completed',
            'approved_by': self.env.user.id,
            'approval_date': fields.Date.today()
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Performance Completed',
                'message': f'Performance "{self.name}" marked as completed',
                'type': 'success'
            }
        }

    def action_request_feedback(self):
        """Request feedback from instructor/peers"""
        # This could be enhanced with actual notification/email functionality
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Feedback Request Sent',
                'message': f'Feedback request sent for performance "{self.name}"',
                'type': 'info'
            }
        }


class ArtistPerformanceSkill(models.Model):
    _name = 'artist.performance.skill'
    _description = 'Skills Demonstrated in Performance'
    _rec_name = 'skill_name'

    performance_id = fields.Many2one('artist.performance.metric', string='Performance', required=True)
    skill_name = fields.Char('Skill Name', required=True)
    skill_category = fields.Selection([
        ('technical', 'Technical Skill'),
        ('artistic', 'Artistic Expression'),
        ('performance', 'Performance Skill'),
        ('collaboration', 'Collaboration'),
        ('leadership', 'Leadership'),
        ('innovation', 'Innovation')
    ], string='Skill Category')
    
    proficiency_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('developing', 'Developing'),
        ('competent', 'Competent'),
        ('proficient', 'Proficient'),
        ('expert', 'Expert')
    ], string='Proficiency Level')
    
    improvement_noted = fields.Boolean('Improvement Noted')
    notes = fields.Text('Notes')