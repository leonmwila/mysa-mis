from odoo import models, fields, api
from datetime import datetime, timedelta


class YouthProgram(models.Model):
    _name = 'youth.program'
    _description = 'Youth Programs & Training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, name'

    name = fields.Char(
        string='Program Name',
        required=True,
        tracking=True
    )
    program_id = fields.Char(
        string='Program ID',
        required=True,
        copy=False,
        readonly=True,
        default='NEW'
    )
    
    # Program Type & Category
    program_type = fields.Selection([
        ('skills_training', 'Skills Training'),
        ('empowerment', 'Youth Empowerment'),
        ('entrepreneurship', 'Entrepreneurship Training'),
        ('leadership', 'Leadership Development'),
        ('mentorship', 'Mentorship Program'),
        ('internship', 'Internship Program'),
        ('scholarship', 'Scholarship Program'),
        ('cdf_program', 'CDF Program'),
        ('sports_program', 'Sports Program'),
        ('arts_program', 'Arts & Culture Program'),
        ('health_program', 'Health & Wellness Program'),
        ('education', 'Educational Support'),
        ('job_creation', 'Job Creation Initiative'),
        ('other', 'Other')
    ], string='Program Type', required=True, tracking=True)
    
    category = fields.Selection([
        ('government', 'Government Program'),
        ('ngo', 'NGO Program'),
        ('private', 'Private Sector Program'),
        ('international', 'International Program'),
        ('community', 'Community Program')
    ], string='Program Category', required=True, default='government')
    
    # Program Details
    description = fields.Text(
        string='Program Description',
        required=True
    )
    objectives = fields.Text(
        string='Program Objectives',
        help='Key objectives and expected outcomes'
    )
    target_beneficiaries = fields.Text(
        string='Target Beneficiaries',
        help='Description of target youth demographic'
    )
    
    # Duration & Schedule
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True
    )
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration'
    )
    is_ongoing = fields.Boolean(
        string='Ongoing Program',
        compute='_compute_program_status'
    )
    
    # Location & Organization
    zone_id = fields.Many2one(
        'youth.zone',
        string='Implementation Zone',
        required=True,
        tracking=True
    )
    venue = fields.Char(
        string='Venue/Location',
        help='Physical location where program is conducted'
    )
    organizing_body_id = fields.Many2one(
        'youth.organization',
        string='Organizing Body',
        help='Organization responsible for implementing the program'
    )
    
    # Participation & Capacity
    max_participants = fields.Integer(
        string='Maximum Participants',
        default=50,
        help='Maximum number of participants allowed'
    )
    participant_ids = fields.Many2many(
        'youth.youth',
        string='Participants',
        help='Youth enrolled in the program'
    )
    current_participants = fields.Integer(
        string='Current Participants',
        compute='_compute_participant_stats'
    )
    available_slots = fields.Integer(
        string='Available Slots',
        compute='_compute_participant_stats'
    )
    
    # Requirements & Eligibility
    age_min = fields.Integer(
        string='Minimum Age',
        default=18,
        help='Minimum age requirement for participation'
    )
    age_max = fields.Integer(
        string='Maximum Age',
        default=35,
        help='Maximum age requirement for participation'
    )
    education_requirements = fields.Text(
        string='Education Requirements',
        help='Minimum education requirements'
    )
    other_requirements = fields.Text(
        string='Other Requirements',
        help='Additional requirements for participation'
    )
    
    # Financial & Resources
    budget = fields.Float(
        string='Program Budget',
        help='Total budget allocated for the program'
    )
    cost_per_participant = fields.Float(
        string='Cost per Participant',
        compute='_compute_cost_per_participant'
    )
    funding_source = fields.Text(
        string='Funding Source',
        help='Source of funding for the program'
    )
    
    # Status & Progress
    status = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended')
    ], string='Status', required=True, default='draft', tracking=True)
    
    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_completion_stats'
    )
    graduation_rate = fields.Float(
        string='Graduation Rate (%)',
        compute='_compute_completion_stats'
    )
    
    # Program Coordination
    coordinator_id = fields.Many2one(
        'res.users',
        string='Program Coordinator',
        required=True,
        help='Person responsible for coordinating the program'
    )
    facilitator_ids = fields.Many2many(
        'res.users',
        string='Facilitators',
        help='Trainers or facilitators for the program'
    )
    
    # Outcomes & Impact
    expected_outcomes = fields.Text(
        string='Expected Outcomes',
        help='Expected results and impact of the program'
    )
    actual_outcomes = fields.Text(
        string='Actual Outcomes',
        help='Actual results achieved by the program'
    )
    success_stories = fields.Text(
        string='Success Stories',
        help='Notable success stories from participants'
    )
    
    # Certification & Recognition
    provides_certificate = fields.Boolean(
        string='Provides Certificate',
        default=True,
        help='Whether the program provides completion certificates'
    )
    certificate_template = fields.Binary(
        string='Certificate Template',
        attachment=True
    )
    
    # Additional Information
    image = fields.Binary(string='Program Image', attachment=True)
    attachments = fields.Text(
        string='Additional Resources',
        help='Links to additional resources or materials'
    )
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    # Event Integration Fields
    event_participants_ids = fields.Many2many(
        'event.program',
        string='Event Participations',
        compute='_compute_event_participants'
    )

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Compute program duration in days"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_days = delta.days + 1
            else:
                record.duration_days = 0

    @api.depends('start_date', 'end_date', 'status')
    def _compute_program_status(self):
        """Compute if program is currently ongoing"""
        today = fields.Date.context_today(self)
        for record in self:
            if (record.start_date and record.end_date and
                record.start_date <= today <= record.end_date and
                record.status == 'active'):
                record.is_ongoing = True
            else:
                record.is_ongoing = False

    @api.depends('participant_ids', 'max_participants')
    def _compute_participant_stats(self):
        """Compute participant statistics"""
        for record in self:
            current = len(record.participant_ids)
            record.current_participants = current
            record.available_slots = record.max_participants - current

    @api.depends('budget', 'current_participants')
    def _compute_cost_per_participant(self):
        """Compute cost per participant"""
        for record in self:
            if record.current_participants > 0 and record.budget > 0:
                record.cost_per_participant = record.budget / record.current_participants
            else:
                record.cost_per_participant = 0.0

    def _compute_completion_stats(self):
        """Compute completion and graduation rates"""
        for record in self:
            if record.status == 'completed' and record.participant_ids:
                # For demonstration, assume all participants complete
                # In real implementation, this would track individual completion
                total_participants = len(record.participant_ids)
                completed_participants = len(record.participant_ids.filtered(
                    lambda p: p.status in ['active', 'graduated']
                ))
                
                record.completion_rate = (completed_participants / total_participants * 100) if total_participants > 0 else 0.0
                record.graduation_rate = record.completion_rate  # Simplified for demo
            else:
                record.completion_rate = 0.0
                record.graduation_rate = 0.0

    def _compute_event_participants(self):
        """Compute method for event participants compatibility"""
        for record in self:
            record.event_participants_ids = [(6, 0, [record.id])]

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'program_id' not in vals_list or not vals_list['program_id']:
                vals_list['program_id'] = self.env['ir.sequence'].next_by_code('youth.program') or 'YPROG000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'program_id' not in vals or not vals['program_id']:
                    vals['program_id'] = self.env['ir.sequence'].next_by_code('youth.program') or 'YPROG000'
        
        return super(YouthProgram, self).create(vals_list)

    def action_start_program(self):
        """Start the program"""
        for record in self:
            record.status = 'active'
            record.message_post(
                body=f"Program {record.name} has been started",
                subject="Program Started"
            )

    def action_complete_program(self):
        """Complete the program"""
        for record in self:
            record.status = 'completed'
            record.message_post(
                body=f"Program {record.name} has been completed",
                subject="Program Completed"
            )

    def action_enroll_youth(self):
        """Action to enroll youth in the program"""
        return {
            'name': 'Enroll Youth',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program.enrollment.wizard',
            'view_mode': 'form',
            'context': {'default_program_id': self.id},
            'target': 'new',
        }

    def action_view_participants(self):
        """Action to view program participants"""
        return {
            'name': f'Participants - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.participant_ids.ids)],
            'target': 'current',
        }

    def action_generate_certificates(self):
        """Action to generate completion certificates"""
        return {
            'name': 'Generate Certificates',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.certificate.wizard',
            'view_mode': 'form',
            'context': {'default_program_id': self.id},
            'target': 'new',
        }

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate program dates"""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise models.ValidationError("Start date cannot be later than end date.")

    @api.constrains('age_min', 'age_max')
    def _check_age_requirements(self):
        """Validate age requirements"""
        for record in self:
            if record.age_min and record.age_max:
                if record.age_min > record.age_max:
                    raise models.ValidationError("Minimum age cannot be greater than maximum age.")