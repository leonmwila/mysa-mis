from odoo import models, fields, api


class YouthOrganization(models.Model):
    _name = 'youth.organization'
    _description = 'Youth Organizations & Groups'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Organization Name',
        required=True,
        tracking=True
    )
    organization_id = fields.Char(
        string='Organization ID',
        required=True,
        copy=False,
        readonly=True,
        default='NEW'
    )
    
    # Organization Type & Category
    organization_type = fields.Selection([
        ('youth_club', 'Youth Club'),
        ('sports_club', 'Youth Sports Club'),
        ('cultural_group', 'Cultural Group'),
        ('church_group', 'Church Youth Group'),
        ('school_group', 'School Youth Group'),
        ('community_group', 'Community Youth Group'),
        ('cooperative', 'Youth Cooperative'),
        ('cbo', 'Community Based Organization'),
        ('ngo', 'Non-Governmental Organization'),
        ('other', 'Other')
    ], string='Organization Type', required=True, tracking=True)
    
    focus_areas = fields.Many2many(
        'youth.specialization',
        string='Focus Areas',
        help='Areas of focus or specialization'
    )
    
    # Registration & Legal
    registration_status = fields.Selection([
        ('pending', 'Registration Pending'),
        ('registered', 'Registered'),
        ('certified', 'Certified'),
        ('suspended', 'Suspended'),
        ('deregistered', 'Deregistered')
    ], string='Registration Status', required=True, default='pending', tracking=True)
    
    registration_number = fields.Char(
        string='Registration Number',
        help='Official registration number with relevant authorities'
    )
    registration_date = fields.Date(
        string='Registration Date',
        default=fields.Date.context_today,
        tracking=True
    )
    
    # Location & Contact
    zone_id = fields.Many2one(
        'youth.zone',
        string='Zone',
        required=True,
        tracking=True
    )
    physical_address = fields.Text(string='Physical Address', required=True)
    postal_address = fields.Text(string='Postal Address')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email Address')
    website = fields.Char(string='Website')
    
    # Leadership
    chairperson_id = fields.Many2one(
        'youth.youth',
        string='Chairperson',
        help='Organization chairperson or leader'
    )
    secretary_id = fields.Many2one(
        'youth.youth',
        string='Secretary',
        help='Organization secretary'
    )
    treasurer_id = fields.Many2one(
        'youth.youth',
        string='Treasurer',
        help='Organization treasurer'
    )
    
    # Membership
    member_ids = fields.Many2many(
        'youth.youth',
        string='Members',
        help='Youth members of the organization'
    )
    total_members = fields.Integer(
        string='Total Members',
        compute='_compute_membership_stats'
    )
    active_members = fields.Integer(
        string='Active Members',
        compute='_compute_membership_stats'
    )
    
    # Programs & Activities
    program_ids = fields.One2many(
        'youth.program',
        'organizing_body_id',
        string='Organized Programs'
    )
    total_programs = fields.Integer(
        string='Total Programs',
        compute='_compute_program_stats'
    )
    active_programs = fields.Integer(
        string='Active Programs',
        compute='_compute_program_stats'
    )
    
    # Financial Information
    annual_budget = fields.Float(string='Annual Budget')
    funding_sources = fields.Text(
        string='Funding Sources',
        help='Description of funding sources and sponsors'
    )
    
    # Performance & Impact
    achievements = fields.Text(
        string='Key Achievements',
        help='Notable achievements and milestones'
    )
    impact_description = fields.Text(
        string='Community Impact',
        help='Description of impact on youth and community'
    )
    
    # Ministry Integration
    ministry_approved = fields.Boolean(
        string='Ministry Approved',
        default=False,
        tracking=True
    )
    approval_date = fields.Date(string='Approval Date')
    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        help='Ministry official who approved the organization'
    )
    
    # Status & Tracking
    active = fields.Boolean(default=True)
    established_date = fields.Date(
        string='Established Date',
        required=True,
        default=fields.Date.context_today
    )
    
    # Additional Information
    logo = fields.Binary(string='Organization Logo', attachment=True)
    description = fields.Text(string='Organization Description')
    vision = fields.Text(string='Vision Statement')
    mission = fields.Text(string='Mission Statement')
    objectives = fields.Text(string='Objectives')
    
    # Event Integration Fields
    event_participants_ids = fields.Many2many(
        'event.program',
        string='Event Participations',
        compute='_compute_event_participants'
    )

    @api.depends('member_ids', 'member_ids.status')
    def _compute_membership_stats(self):
        """Compute membership statistics"""
        for record in self:
            members = record.member_ids
            record.total_members = len(members)
            record.active_members = len(members.filtered(lambda m: m.status == 'active'))

    @api.depends('program_ids', 'program_ids.status')
    def _compute_program_stats(self):
        """Compute program statistics"""
        for record in self:
            programs = record.program_ids
            record.total_programs = len(programs)
            record.active_programs = len(programs.filtered(lambda p: p.status == 'active'))

    def _compute_event_participants(self):
        """Compute method for event participants compatibility"""
        for record in self:
            record.event_participants_ids = [(6, 0, [record.id])]

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            # Single record creation
            if 'organization_id' not in vals_list or not vals_list['organization_id']:
                vals_list['organization_id'] = self.env['ir.sequence'].next_by_code('youth.organization') or 'YORG000'
        else:
            # Batch creation - list of dicts
            for vals in vals_list:
                if 'organization_id' not in vals or not vals['organization_id']:
                    vals['organization_id'] = self.env['ir.sequence'].next_by_code('youth.organization') or 'YORG000'
        
        return super(YouthOrganization, self).create(vals_list)

    def action_approve_organization(self):
        """Approve organization for ministry recognition"""
        for record in self:
            record.ministry_approved = True
            record.approval_date = fields.Date.context_today(self)
            record.approver_id = self.env.user.id
            record.registration_status = 'certified'
            
            # Log approval in chatter
            record.message_post(
                body=f"Organization {record.name} has been approved by {self.env.user.name}",
                subject="Organization Approved"
            )

    def action_suspend_organization(self):
        """Suspend organization"""
        for record in self:
            record.registration_status = 'suspended'
            record.active = False
            
            # Log suspension in chatter
            record.message_post(
                body=f"Organization {record.name} has been suspended",
                subject="Organization Suspended"
            )

    def action_view_members(self):
        """Action to view organization members"""
        return {
            'name': f'Members - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,list,form',
            'domain': [('organization_ids', 'in', [self.id])],
            'target': 'current',
        }

    def action_view_programs(self):
        """Action to view organization programs"""
        return {
            'name': f'Programs - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program',
            'view_mode': 'kanban,list,form',
            'domain': [('organizing_body_id', '=', self.id)],
            'context': {'default_organizing_body_id': self.id},
            'target': 'current',
        }

    def action_add_members(self):
        """Action to add new members to the organization"""
        return {
            'name': 'Add Members',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.organization.member.wizard',
            'view_mode': 'form',
            'context': {'default_organization_id': self.id},
            'target': 'new',
        }