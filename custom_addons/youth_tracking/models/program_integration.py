from odoo import models, fields, api


class EventProgramYouthIntegration(models.Model):
    _inherit = 'event.program'

    # Youth Program Integration
    youth_participant_count = fields.Integer(
        string='Youth Participants',
        compute='_compute_youth_participant_count',
        store=True
    )
    youth_participants_ids = fields.Many2many(
        'youth.youth',
        string='Youth Participants',
        help='Youth participants in this event/program'
    )
    
    # Youth-specific event fields
    is_youth_event = fields.Boolean(
        string='Youth Event',
        help='Mark if this is primarily a youth-focused event'
    )
    youth_age_min = fields.Integer(
        string='Min Age for Youth',
        default=18,
        help='Minimum age for youth participation'
    )
    youth_age_max = fields.Integer(
        string='Max Age for Youth',
        default=35,
        help='Maximum age for youth participation'
    )
    
    # Program categories relevant to youth
    youth_program_type = fields.Selection([
        ('skills_training', 'Skills Training'),
        ('empowerment', 'Youth Empowerment'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('leadership', 'Leadership Development'),
        ('sports', 'Sports Program'),
        ('arts_culture', 'Arts & Culture'),
        ('community_service', 'Community Service'),
        ('health_wellness', 'Health & Wellness'),
        ('education', 'Educational Program'),
        ('other', 'Other')
    ], string='Youth Program Type')

    @api.depends('youth_participants_ids')
    def _compute_youth_participant_count(self):
        """Compute number of youth participants"""
        for record in self:
            record.youth_participant_count = len(record.youth_participants_ids)

    def action_select_youth_participants(self):
        """Action to select youth participants for the event"""
        return {
            'name': 'Select Youth Participants',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.participant.selector.wizard',
            'view_mode': 'form',
            'context': {
                'default_event_id': self.id,
                'default_age_min': self.youth_age_min,
                'default_age_max': self.youth_age_max,
            },
            'target': 'new',
        }

    def action_view_youth_participants(self):
        """View youth participants in this event"""
        return {
            'name': f'Youth Participants - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.youth_participants_ids.ids)],
            'target': 'current',
        }


class YouthParticipantSelectorWizard(models.TransientModel):
    _name = 'youth.participant.selector.wizard'
    _description = 'Youth Participant Selection Wizard'

    event_id = fields.Many2one('event.program', string='Event', required=True)
    zone_id = fields.Many2one('youth.zone', string='Filter by Zone')
    age_min = fields.Integer(string='Minimum Age', default=18)
    age_max = fields.Integer(string='Maximum Age', default=35)
    
    # Selection criteria
    education_level = fields.Selection([
        ('primary', 'Primary Education'),
        ('secondary', 'Secondary Education'),
        ('tertiary', 'Tertiary Education'),
        ('university', 'University'),
        ('vocational', 'Vocational Training'),
    ], string='Education Level Filter')
    
    employment_status = fields.Selection([
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
    ], string='Employment Status Filter')
    
    # Available and selected youth
    available_youth_ids = fields.Many2many(
        'youth.youth',
        'wizard_available_youth_rel',
        string='Available Youth',
        compute='_compute_available_youth'
    )
    selected_youth_ids = fields.Many2many(
        'youth.youth',
        'wizard_selected_youth_rel',
        string='Selected Youth'
    )

    @api.depends('zone_id', 'age_min', 'age_max', 'education_level', 'employment_status')
    def _compute_available_youth(self):
        """Compute available youth based on criteria"""
        for wizard in self:
            domain = [('status', '=', 'active')]
            
            if wizard.zone_id:
                domain.append(('zone_id', '=', wizard.zone_id.id))
            if wizard.age_min:
                domain.append(('age', '>=', wizard.age_min))
            if wizard.age_max:
                domain.append(('age', '<=', wizard.age_max))
            if wizard.education_level:
                domain.append(('education_level', '=', wizard.education_level))
            if wizard.employment_status:
                domain.append(('employment_status', '=', wizard.employment_status))
            
            available_youth = self.env['youth.youth'].search(domain)
            wizard.available_youth_ids = [(6, 0, available_youth.ids)]

    def action_confirm_selection(self):
        """Confirm youth selection for the event"""
        if self.selected_youth_ids:
            # Add selected youth to the event
            self.event_id.write({
                'youth_participants_ids': [(6, 0, self.selected_youth_ids.ids)]
            })
            
            # Create activity records for tracking
            for youth in self.selected_youth_ids:
                youth.message_post(
                    body=f"Selected for event: {self.event_id.name}",
                    subject="Event Participation"
                )
        
        return {'type': 'ir.actions.act_window_close'}


class YouthAchievement(models.Model):
    _name = 'youth.achievement'
    _description = 'Youth Achievements & Recognition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'achievement_date desc'

    name = fields.Char(
        string='Achievement Title',
        required=True,
        tracking=True
    )
    youth_id = fields.Many2one(
        'youth.youth',
        string='Youth',
        required=True,
        tracking=True
    )
    
    # Achievement Details
    achievement_type = fields.Selection([
        ('program_completion', 'Program Completion'),
        ('certification', 'Certification'),
        ('award', 'Award/Recognition'),
        ('competition', 'Competition Win'),
        ('leadership', 'Leadership Role'),
        ('community_service', 'Community Service'),
        ('entrepreneurship', 'Business Success'),
        ('academic', 'Academic Achievement'),
        ('skills', 'Skills Demonstration'),
        ('other', 'Other')
    ], string='Achievement Type', required=True, tracking=True)
    
    description = fields.Text(
        string='Achievement Description',
        required=True
    )
    achievement_level = fields.Selection([
        ('local', 'Local Level'),
        ('district', 'District Level'),
        ('provincial', 'Provincial Level'),
        ('national', 'National Level'),
        ('international', 'International Level')
    ], string='Achievement Level', required=True, default='local')
    
    # Dates and Verification
    achievement_date = fields.Date(
        string='Achievement Date',
        required=True,
        default=fields.Date.context_today
    )
    
    # Associated Program or Event
    program_id = fields.Many2one(
        'youth.program',
        string='Related Program',
        help='Program associated with this achievement'
    )
    event_id = fields.Many2one(
        'event.program',
        string='Related Event',
        help='Event associated with this achievement'
    )
    
    # Recognition and Awards
    award_given_by = fields.Char(
        string='Awarded By',
        help='Organization or person who gave the award'
    )
    certificate_issued = fields.Boolean(
        string='Certificate Issued',
        default=False
    )
    certificate_number = fields.Char(string='Certificate Number')
    
    # Verification
    verified = fields.Boolean(
        string='Verified',
        default=False,
        tracking=True
    )
    verified_by_id = fields.Many2one(
        'res.users',
        string='Verified By'
    )
    verification_date = fields.Date(string='Verification Date')
    
    # Impact and Recognition Value
    points_awarded = fields.Integer(
        string='Points Awarded',
        default=0,
        help='Points awarded for this achievement in youth scoring system'
    )
    
    # Additional Information
    notes = fields.Text(string='Notes')
    attachments_count = fields.Integer(
        string='Attachments',
        compute='_compute_attachments_count'
    )
    active = fields.Boolean(default=True)

    @api.depends('message_attachment_count')
    def _compute_attachments_count(self):
        """Compute number of attachments"""
        for record in self:
            record.attachments_count = record.message_attachment_count

    def action_verify_achievement(self):
        """Verify the achievement"""
        for record in self:
            record.verified = True
            record.verified_by_id = self.env.user.id
            record.verification_date = fields.Date.context_today(self)
            record.message_post(
                body=f"Achievement verified by {self.env.user.name}",
                subject="Achievement Verified"
            )

    def action_issue_certificate(self):
        """Issue certificate for achievement"""
        for record in self:
            record.certificate_issued = True
            # Generate certificate number if not exists
            if not record.certificate_number:
                record.certificate_number = f"CERT-{record.id:06d}"
            record.message_post(
                body=f"Certificate {record.certificate_number} issued for achievement",
                subject="Certificate Issued"
            )