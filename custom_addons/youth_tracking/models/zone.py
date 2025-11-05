from odoo import models, fields, api


class YouthZone(models.Model):
    _name = 'youth.zone'
    _description = 'Youth Geographical Zone Management'
    _order = 'name'

    name = fields.Char(
        string='Zone Name',
        required=True,
        help='Geographical zone or district name'
    )
    zone_code = fields.Char(
        string='Zone Code',
        required=True,
        copy=False,
        help='Unique code for the zone'
    )
    zone_type = fields.Selection([
        ('district', 'District'),
        ('constituency', 'Constituency'),
        ('ward', 'Ward'),
        ('community', 'Community'),
        ('urban', 'Urban Area'),
        ('rural', 'Rural Area')
    ], string='Zone Type', required=True, default='district')
    
    # Location Details
    province = fields.Char(string='Province', required=True)
    parent_zone_id = fields.Many2one(
        'youth.zone',
        string='Parent Zone',
        help='Higher level administrative zone'
    )
    child_zone_ids = fields.One2many(
        'youth.zone',
        'parent_zone_id',
        string='Sub-zones'
    )
    
    # Contact Information
    coordinator_id = fields.Many2one(
        'res.users',
        string='Youth Coordinator',
        help='Provincial Youth Development Coordinator (PYDC) or local coordinator'
    )
    coordinator_phone = fields.Char(
        string='Coordinator Phone',
        related='coordinator_id.phone'
    )
    coordinator_email = fields.Char(
        string='Coordinator Email',
        related='coordinator_id.email'
    )
    
    # Zone Statistics
    youth_count = fields.Integer(
        string='Total Youth',
        compute='_compute_youth_stats'
    )
    active_youth_count = fields.Integer(
        string='Active Youth',
        compute='_compute_youth_stats'
    )
    program_count = fields.Integer(
        string='Active Programs',
        compute='_compute_program_stats'
    )
    organization_count = fields.Integer(
        string='Youth Organizations',
        compute='_compute_organization_stats'
    )
    
    # Performance Metrics
    total_applications = fields.Integer(
        string='Total Applications',
        compute='_compute_application_stats'
    )
    approved_applications = fields.Integer(
        string='Approved Applications',
        compute='_compute_application_stats'
    )
    success_rate = fields.Float(
        string='Approval Success Rate (%)',
        compute='_compute_application_stats'
    )
    
    # Financial & Resources
    allocated_budget = fields.Float(
        string='Allocated Budget',
        help='Budget allocated for youth programs in this zone'
    )
    utilized_budget = fields.Float(
        string='Utilized Budget',
        compute='_compute_budget_utilization'
    )
    budget_utilization_rate = fields.Float(
        string='Budget Utilization (%)',
        compute='_compute_budget_utilization'
    )
    
    # Additional Information
    description = fields.Text(string='Zone Description')
    population = fields.Integer(string='Total Population')
    youth_population_estimate = fields.Integer(
        string='Estimated Youth Population',
        help='Estimated number of youth (18-35) in the zone'
    )
    
    # Status
    active = fields.Boolean(default=True)
    established_date = fields.Date(
        string='Zone Established Date',
        default=fields.Date.context_today
    )

    @api.depends('youth_count', 'active_youth_count')
    def _compute_youth_stats(self):
        """Compute youth statistics for the zone"""
        Youth = self.env['youth.youth']
        for record in self:
            youth_in_zone = Youth.search([('zone_id', '=', record.id)])
            record.youth_count = len(youth_in_zone)
            record.active_youth_count = len(youth_in_zone.filtered(lambda y: y.status == 'active'))

    def _compute_program_stats(self):
        """Compute program statistics for the zone"""
        Program = self.env['youth.program']
        for record in self:
            programs = Program.search([('zone_id', '=', record.id), ('status', '=', 'active')])
            record.program_count = len(programs)

    def _compute_organization_stats(self):
        """Compute organization statistics for the zone"""
        Organization = self.env['youth.organization']
        for record in self:
            organizations = Organization.search([('zone_id', '=', record.id), ('active', '=', True)])
            record.organization_count = len(organizations)

    def _compute_application_stats(self):
        """Compute application statistics for the zone"""
        Application = self.env['youth.application']
        for record in self:
            # Get all applications from youth in this zone
            youth_ids = self.env['youth.youth'].search([('zone_id', '=', record.id)]).ids
            applications = Application.search([('youth_id', 'in', youth_ids)])
            
            total = len(applications)
            approved = len(applications.filtered(lambda a: a.status == 'approved'))
            
            record.total_applications = total
            record.approved_applications = approved
            record.success_rate = (approved / total * 100) if total > 0 else 0.0

    def _compute_budget_utilization(self):
        """Compute budget utilization for the zone"""
        Application = self.env['youth.application']
        for record in self:
            # Calculate utilized budget from approved applications
            youth_ids = self.env['youth.youth'].search([('zone_id', '=', record.id)]).ids
            approved_apps = Application.search([
                ('youth_id', 'in', youth_ids),
                ('status', '=', 'approved')
            ])
            
            utilized = sum(approved_apps.mapped('approved_amount'))
            record.utilized_budget = utilized
            record.budget_utilization_rate = (
                (utilized / record.allocated_budget * 100) 
                if record.allocated_budget > 0 else 0.0
            )

    def action_view_youth(self):
        """Action to view youth in this zone"""
        return {
            'name': f'Youth in {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,list,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id},
            'target': 'current',
        }

    def action_view_programs(self):
        """Action to view programs in this zone"""
        return {
            'name': f'Programs in {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program',
            'view_mode': 'kanban,list,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id},
            'target': 'current',
        }

    def action_view_organizations(self):
        """Action to view organizations in this zone"""
        return {
            'name': f'Organizations in {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.organization',
            'view_mode': 'kanban,list,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id},
            'target': 'current',
        }

    def action_zone_dashboard(self):
        """Action to view zone dashboard"""
        return {
            'name': f'{self.name} - Dashboard',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.analytics',
            'view_mode': 'form',
            'context': {
                'default_zone_id': self.id,
                'zone_dashboard': True
            },
            'target': 'current',
        }