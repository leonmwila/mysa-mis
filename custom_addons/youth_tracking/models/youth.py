from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class Youth(models.Model):
    _name = 'youth.youth'
    _description = 'Youth Profile & Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'registration_date desc, name'

    # Basic Information
    youth_id = fields.Char(
        string='Youth ID',
        required=True,
        copy=False,
        readonly=True,
        default='NEW'
    )
    name = fields.Char(
        string='Full Name',
        required=True,
        tracking=True
    )
    stage_name = fields.Char(
        string='Preferred Name',
        help='Name commonly used or preferred'
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
        required=True,
        tracking=True
    )
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', required=True, tracking=True)
    
    # Contact Information
    phone = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email Address')
    address = fields.Text(string='Physical Address', required=True)
    nrc_number = fields.Char(string='NRC Number', help='National Registration Card')
    emergency_contact = fields.Char(string='Emergency Contact Name')
    emergency_phone = fields.Char(string='Emergency Contact Phone')
    
    # Educational Background
    education_level = fields.Selection([
        ('primary', 'Primary Education'),
        ('secondary', 'Secondary Education'),
        ('tertiary', 'Tertiary Education'),
        ('university', 'University'),
        ('vocational', 'Vocational Training'),
        ('other', 'Other')
    ], string='Education Level', required=True)
    current_institution = fields.Char(string='Current Institution/School')
    grade_year = fields.Char(string='Grade/Year')
    graduation_date = fields.Date(string='Expected/Actual Graduation Date')
    
    # Youth Development
    employment_status = fields.Selection([
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('volunteer', 'Volunteer Work')
    ], string='Employment Status', required=True, default='unemployed')
    skills_interests = fields.Text(string='Skills & Interests', help='Areas of interest and existing skills')
    career_aspirations = fields.Text(string='Career Aspirations')
    
    # Location & Organization
    zone_id = fields.Many2one(
        'youth.zone',
        string='Youth Zone',
        required=True,
        tracking=True
    )
    organization_ids = fields.Many2many(
        'youth.organization',
        string='Youth Organizations',
        help='Youth groups, clubs, or organizations the youth belongs to'
    )
    
    # Program Participation
    program_ids = fields.Many2many(
        'youth.program',
        string='Enrolled Programs',
        readonly=True
    )
    active_programs = fields.Integer(
        string='Active Programs',
        compute='_compute_program_stats'
    )
    completed_programs = fields.Integer(
        string='Completed Programs',
        compute='_compute_program_stats'
    )
    
    # Status & Tracking
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('suspended', 'Suspended')
    ], string='Status', required=True, default='active', tracking=True)
    
    registration_date = fields.Date(
        string='Registration Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    # Analytics & Performance
    total_applications = fields.Integer(
        string='Total Applications',
        compute='_compute_application_stats'
    )
    approved_applications = fields.Integer(
        string='Approved Applications',
        compute='_compute_application_stats'
    )
    application_success_rate = fields.Float(
        string='Application Success Rate (%)',
        compute='_compute_application_stats'
    )
    last_activity_date = fields.Date(
        string='Last Activity',
        compute='_compute_last_activity'
    )
    
    # CDF & Financial Support
    cdf_eligible = fields.Boolean(
        string='CDF Eligible',
        default=True,
        help='Eligible for Constituency Development Fund support'
    )
    financial_support_received = fields.Float(
        string='Total Financial Support Received',
        compute='_compute_financial_stats'
    )
    
    # Additional Information
    image = fields.Binary(string='Photo', attachment=True)
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)
    
    # Event Integration Fields (for compatibility with event management)
    event_participants_ids = fields.Many2many(
        'event.program',
        string='Event Participations',
        compute='_compute_event_participants'
    )

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calculate age from date of birth"""
        for record in self:
            if record.date_of_birth:
                record.age = relativedelta(date.today(), record.date_of_birth).years
            else:
                record.age = 0

    @api.depends('program_ids', 'program_ids.status')
    def _compute_program_stats(self):
        """Compute program participation statistics"""
        for record in self:
            programs = record.program_ids
            record.active_programs = len(programs.filtered(lambda p: p.status == 'active'))
            record.completed_programs = len(programs.filtered(lambda p: p.status == 'completed'))

    def _compute_application_stats(self):
        """Compute application statistics"""
        Application = self.env['youth.application']
        for record in self:
            applications = Application.search([('youth_id', '=', record.id)])
            total = len(applications)
            approved = len(applications.filtered(lambda a: a.status == 'approved'))
            
            record.total_applications = total
            record.approved_applications = approved
            record.application_success_rate = (approved / total * 100) if total > 0 else 0.0

    def _compute_last_activity(self):
        """Compute last activity date"""
        for record in self:
            # Check latest application, program enrollment, or any activity
            latest_date = record.registration_date
            if record.program_ids:
                program_dates = record.program_ids.mapped('start_date')
                if program_dates:
                    latest_program = max(program_dates)
                    if latest_program > latest_date:
                        latest_date = latest_program
            record.last_activity_date = latest_date

    def _compute_financial_stats(self):
        """Compute financial support statistics"""
        Application = self.env['youth.application']
        for record in self:
            approved_apps = Application.search([
                ('youth_id', '=', record.id),
                ('status', '=', 'approved'),
                ('application_type', 'in', ['cdf', 'financial_support'])
            ])
            record.financial_support_received = sum(approved_apps.mapped('requested_amount'))

    def _compute_event_participants(self):
        """Compute method for event participants compatibility"""
        for record in self:
            record.event_participants_ids = [(6, 0, [record.id])]

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'youth_id' not in vals_list or not vals_list['youth_id']:
                vals_list['youth_id'] = self.env['ir.sequence'].next_by_code('youth.youth') or 'YOUTH000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'youth_id' not in vals or not vals['youth_id']:
                    vals['youth_id'] = self.env['ir.sequence'].next_by_code('youth.youth') or 'YOUTH000'
        
        return super(Youth, self).create(vals_list)

    def action_view_applications(self):
        """Action to view youth's applications"""
        return {
            'name': f'Applications - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.application',
            'view_mode': 'list,form',
            'domain': [('youth_id', '=', self.id)],
            'context': {'default_youth_id': self.id},
            'target': 'current',
        }

    def action_view_programs(self):
        """Action to view youth's programs"""
        return {
            'name': f'Programs - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program',
            'view_mode': 'list,form',
            'domain': [('participant_ids', 'in', [self.id])],
            'target': 'current',
        }

    def action_enroll_program(self):
        """Action to enroll in a new program"""
        return {
            'name': 'Enroll in Program',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program.enrollment.wizard',
            'view_mode': 'form',
            'context': {'default_youth_id': self.id},
            'target': 'new',
        }

    def toggle_cdf_eligibility(self):
        """Toggle CDF eligibility status"""
        for record in self:
            record.cdf_eligible = not record.cdf_eligible
            
    def action_graduate(self):
        """Mark youth as graduated"""
        for record in self:
            record.status = 'graduated'
            # Log graduation in chatter
            record.message_post(
                body=f"Youth {record.name} has been marked as graduated on {fields.Date.today()}",
                subject="Youth Graduation"
            )

    @api.model
    def get_import_templates(self):
        """Provide import template for youth data"""
        return [{
            'label': 'Import Template for Youth',
            'template': '/youth_tracking/static/xls/youth_import_template.xlsx'
        }]


class YouthSpecialization(models.Model):
    _name = 'youth.specialization'
    _description = 'Youth Skills & Specializations'

    name = fields.Char(string='Specialization', required=True)
    category = fields.Selection([
        ('technical', 'Technical Skills'),
        ('business', 'Business & Entrepreneurship'),
        ('agriculture', 'Agriculture'),
        ('arts_crafts', 'Arts & Crafts'),
        ('ict', 'ICT & Technology'),
        ('health', 'Health & Wellness'),
        ('education', 'Education & Training'),
        ('sports', 'Sports & Recreation'),
        ('other', 'Other')
    ], string='Category', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)