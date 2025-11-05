from odoo import models, fields, api


class YouthApplication(models.Model):
    _name = 'youth.application'
    _description = 'Youth Applications (CDF, Training, Empowerment)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'application_date desc, priority desc'

    name = fields.Char(
        string='Application Title',
        required=True,
        tracking=True
    )
    application_id = fields.Char(
        string='Application ID',
        required=True,
        copy=False,
        readonly=True,
        default='NEW'
    )
    
    # Applicant Information
    youth_id = fields.Many2one(
        'youth.youth',
        string='Applicant',
        required=True,
        tracking=True
    )
    applicant_zone = fields.Many2one(
        'youth.zone',
        string='Applicant Zone',
        related='youth_id.zone_id',
        store=True
    )
    
    # Program Information
    program_id = fields.Many2one(
        'event.program',
        string='Program',
        domain="[('category', '=', 'youth')]",
        help='Youth Development program the applicant is applying for',
        tracking=True
    )
    
    # Application Type & Category
    application_type = fields.Selection([
        ('cdf', 'CDF Application'),
        ('skills_training', 'Skills Training Application'),
        ('empowerment', 'Youth Empowerment Program'),
        ('entrepreneurship', 'Entrepreneurship Support'),
        ('education_support', 'Educational Support'),
        ('financial_support', 'Financial Assistance'),
        ('job_placement', 'Job Placement Support'),
        ('internship', 'Internship Application'),
        ('scholarship', 'Scholarship Application'),
        ('business_support', 'Business Support'),
        ('equipment_support', 'Equipment Support'),
        ('medical_support', 'Medical Assistance'),
        ('emergency_support', 'Emergency Support'),
        ('other', 'Other')
    ], string='Application Type', required=True, tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', required=True, default='medium', tracking=True)
    
    # Application Details
    description = fields.Text(
        string='Application Description',
        required=True,
        help='Detailed description of the application and needs'
    )
    justification = fields.Text(
        string='Justification',
        help='Justification for the application and expected impact'
    )
    objectives = fields.Text(
        string='Objectives',
        help='What the applicant hopes to achieve'
    )
    
    # Financial Information
    requested_amount = fields.Float(
        string='Requested Amount',
        help='Amount of financial support requested'
    )
    approved_amount = fields.Float(
        string='Approved Amount',
        help='Amount approved for disbursement'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Supporting Documents
    supporting_documents = fields.Text(
        string='Supporting Documents',
        help='List of supporting documents submitted'
    )
    attachments_count = fields.Integer(
        string='Attachments',
        compute='_compute_attachments_count'
    )
    
    # Application Dates
    application_date = fields.Date(
        string='Application Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    deadline_date = fields.Date(
        string='Response Deadline',
        help='Deadline for processing the application'
    )
    
    # Status & Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('committee_review', 'Committee Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', required=True, default='draft', tracking=True)
    
    # Approval Workflow
    reviewer_id = fields.Many2one(
        'res.users',
        string='Current Reviewer',
        help='Person currently reviewing the application'
    )
    pydc_approval = fields.Boolean(
        string='PYDC Approved',
        help='Provincial Youth Development Coordinator approval'
    )
    pydc_approver_id = fields.Many2one('res.users', string='PYDC Approver')
    pydc_approval_date = fields.Date(string='PYDC Approval Date')
    
    committee_approval = fields.Boolean(
        string='Committee Approved',
        help='Voting Committee approval'
    )
    committee_approver_id = fields.Many2one('res.users', string='Committee Approver')
    committee_approval_date = fields.Date(string='Committee Approval Date')
    
    director_approval = fields.Boolean(
        string='Director Approved',
        help='HQ Director approval'
    )
    director_approver_id = fields.Many2one('res.users', string='Director Approver')
    director_approval_date = fields.Date(string='Director Approval Date')
    
    final_approval = fields.Boolean(
        string='Final Approval',
        help='Final approval for fund dispensation'
    )
    final_approver_id = fields.Many2one('res.users', string='Final Approver')
    final_approval_date = fields.Date(string='Final Approval Date')
    
    # Review & Feedback
    review_notes = fields.Text(
        string='Review Notes',
        help='Notes and comments from reviewers'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help='Reason for rejection if applicable'
    )
    recommendations = fields.Text(
        string='Recommendations',
        help='Recommendations for improvement or future applications'
    )
    
    # Disbursement & Completion
    disbursement_date = fields.Date(
        string='Disbursement Date',
        help='Date when funds were disbursed'
    )
    disbursed_by_id = fields.Many2one(
        'res.users',
        string='Disbursed By',
        help='Person who processed the disbursement'
    )
    completion_date = fields.Date(
        string='Completion Date',
        help='Date when the application objective was completed'
    )
    
    # Impact & Follow-up
    impact_report = fields.Text(
        string='Impact Report',
        help='Report on the impact and outcomes of the support'
    )
    follow_up_required = fields.Boolean(
        string='Follow-up Required',
        default=True,
        help='Whether follow-up is required to track progress'
    )
    next_follow_up_date = fields.Date(
        string='Next Follow-up Date',
        help='Date for next follow-up or review'
    )
    
    # Additional Information
    notes = fields.Text(string='Additional Notes')
    active = fields.Boolean(default=True)

    @api.depends('message_attachment_count')
    def _compute_attachments_count(self):
        """Compute number of attachments"""
        for record in self:
            record.attachments_count = record.message_attachment_count

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'application_id' not in vals_list or not vals_list['application_id']:
                vals_list['application_id'] = self.env['ir.sequence'].next_by_code('youth.application') or 'YAPP000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'application_id' not in vals or not vals['application_id']:
                    vals['application_id'] = self.env['ir.sequence'].next_by_code('youth.application') or 'YAPP000'
        
        return super(YouthApplication, self).create(vals_list)

    def action_submit_application(self):
        """Submit application for review"""
        for record in self:
            record.status = 'submitted'
            record.message_post(
                body=f"Application {record.name} has been submitted for review",
                subject="Application Submitted"
            )

    def action_start_review(self):
        """Start review process"""
        for record in self:
            record.status = 'under_review'
            record.reviewer_id = self.env.user.id
            record.message_post(
                body=f"Application review started by {self.env.user.name}",
                subject="Review Started"
            )

    def action_pydc_approve(self):
        """PYDC approval"""
        for record in self:
            record.pydc_approval = True
            record.pydc_approver_id = self.env.user.id
            record.pydc_approval_date = fields.Date.context_today(self)
            record.status = 'committee_review'
            record.message_post(
                body=f"PYDC approval granted by {self.env.user.name}",
                subject="PYDC Approved"
            )

    def action_committee_approve(self):
        """Committee approval"""
        try:
            for record in self:
                record.committee_approval = True
                record.committee_approver_id = self.env.user.id
                record.committee_approval_date = fields.Date.context_today(self)
                record.status = 'approved'
                
                # Add youth as participant to the program if a program is selected
                if record.program_id and record.youth_id:
                    # Check if youth is already a participant
                    existing_participant = self.env['event.participant'].search([
                        ('program_id', '=', record.program_id.id),
                        ('name', '=', record.youth_id.name)
                    ], limit=1)
                    
                    if not existing_participant:
                        # Create participant record
                        self.env['event.participant'].create({
                            'name': record.youth_id.name,
                            'program_id': record.program_id.id,
                            'gender': record.youth_id.gender,
                            'contact': record.youth_id.phone,
                            'address': record.youth_id.address,
                        })
                        
                        record.message_post(
                            body=f"Committee approval granted by {self.env.user.name}. Youth {record.youth_id.name} has been added as a participant to program '{record.program_id.name}'.",
                            subject="Committee Approved & Participant Added"
                        )
                    else:
                        record.message_post(
                            body=f"Committee approval granted by {self.env.user.name}. Youth {record.youth_id.name} is already a participant in program '{record.program_id.name}'.",
                            subject="Committee Approved"
                        )
                else:
                    record.message_post(
                        body=f"Committee approval granted by {self.env.user.name}",
                        subject="Committee Approved"
                    )
                
            # Return a notification to confirm the action worked
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': 'Application has been approved by committee.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            # Log the error and show a notification
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in committee approval: {str(e)}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error!',
                    'message': f'Error occurred during approval: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_director_approve(self):
        """Director approval"""
        for record in self:
            record.director_approval = True
            record.director_approver_id = self.env.user.id
            record.director_approval_date = fields.Date.context_today(self)
            record.status = 'disbursed'  # Move to disbursed status after director approval
            record.message_post(
                body=f"Director approval granted by {self.env.user.name}. Status changed to Disbursed.",
                subject="Director Approved"
            )

    def action_final_approve(self):
        """Final approval and mark as approved"""
        for record in self:
            record.final_approval = True
            record.final_approver_id = self.env.user.id
            record.final_approval_date = fields.Date.context_today(self)
            record.status = 'approved'
            record.message_post(
                body=f"Final approval granted by {self.env.user.name}. Application approved for fund dispensation.",
                subject="Final Approval - Ready for Disbursement"
            )

    def action_reject_application(self):
        """Reject application"""
        return {
            'name': 'Reject Application',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.application.reject.wizard',
            'view_mode': 'form',
            'context': {'default_application_id': self.id},
            'target': 'new',
        }

    def action_disburse_funds(self):
        """Disburse approved funds"""
        for record in self:
            if record.status == 'approved':
                record.status = 'disbursed'
                record.disbursement_date = fields.Date.context_today(self)
                record.disbursed_by_id = self.env.user.id
                record.message_post(
                    body=f"Funds disbursed by {self.env.user.name}. Amount: {record.approved_amount}",
                    subject="Funds Disbursed"
                )

    def action_mark_completed(self):
        """Mark application as completed"""
        for record in self:
            record.status = 'completed'
            record.completion_date = fields.Date.context_today(self)
            record.message_post(
                body=f"Application marked as completed",
                subject="Application Completed"
            )

    def action_view_attachments(self):
        """View application attachments"""
        return {
            'name': 'Application Attachments',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('res_model', '=', 'youth.application'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'youth.application',
                'default_res_id': self.id
            },
            'target': 'current',
        }