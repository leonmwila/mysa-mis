from odoo import models, fields, api, tools
from odoo.exceptions import UserError


class YouthAnalytics(models.Model):
    _name = 'youth.analytics'
    _description = 'Youth Analytics & Dashboard'
    _auto = False

    # Dashboard Filters
    zone_id = fields.Many2one('youth.zone', string='Zone Filter')
    date_from = fields.Date(string='Date From', default=fields.Date.context_today)
    date_to = fields.Date(string='Date To', default=fields.Date.context_today)
    
    # Youth Statistics
    total_youth = fields.Integer(string='Total Youth Registered')
    active_youth = fields.Integer(string='Active Youth')
    inactive_youth = fields.Integer(string='Inactive Youth')
    new_registrations_month = fields.Integer(string='New Registrations This Month')
    
    # Age Demographics
    youth_18_25 = fields.Integer(string='Youth 18-25')
    youth_26_30 = fields.Integer(string='Youth 26-30')
    youth_31_35 = fields.Integer(string='Youth 31-35')
    
    # Gender Distribution
    male_youth = fields.Integer(string='Male Youth')
    female_youth = fields.Integer(string='Female Youth')
    gender_ratio = fields.Float(string='Gender Ratio (F/M)')
    
    # Education Levels
    primary_education = fields.Integer(string='Primary Education')
    secondary_education = fields.Integer(string='Secondary Education')
    tertiary_education = fields.Integer(string='Tertiary Education')
    university_education = fields.Integer(string='University Education')
    
    # Employment Status
    employed_youth = fields.Integer(string='Employed Youth')
    unemployed_youth = fields.Integer(string='Unemployed Youth')
    student_youth = fields.Integer(string='Student Youth')
    self_employed_youth = fields.Integer(string='Self-Employed Youth')
    
    # Program Statistics
    total_programs = fields.Integer(string='Total Programs')
    active_programs = fields.Integer(string='Active Programs')
    completed_programs = fields.Integer(string='Completed Programs')
    total_program_participants = fields.Integer(string='Total Program Participants')
    
    # Application Statistics
    total_applications = fields.Integer(string='Total Applications')
    pending_applications = fields.Integer(string='Pending Applications')
    approved_applications = fields.Integer(string='Approved Applications')
    rejected_applications = fields.Integer(string='Rejected Applications')
    application_success_rate = fields.Float(string='Application Success Rate (%)')
    
    # CDF Statistics
    cdf_applications = fields.Integer(string='CDF Applications')
    cdf_approved = fields.Integer(string='CDF Approved')
    cdf_total_amount = fields.Float(string='Total CDF Amount Disbursed')
    cdf_average_amount = fields.Float(string='Average CDF Amount')
    
    # Financial Statistics
    total_budget_allocated = fields.Float(string='Total Budget Allocated')
    total_budget_utilized = fields.Float(string='Total Budget Utilized')
    budget_utilization_rate = fields.Float(string='Budget Utilization Rate (%)')
    
    # Organization Statistics
    total_organizations = fields.Integer(string='Total Youth Organizations')
    active_organizations = fields.Integer(string='Active Organizations')
    registered_organizations = fields.Integer(string='Registered Organizations')
    
    # Zone Performance
    top_performing_zone_id = fields.Many2one('youth.zone', string='Top Performing Zone')
    zone_participation_rate = fields.Float(string='Zone Participation Rate (%)')

    def init(self):
        """Initialize the SQL view for analytics"""
        tools.drop_view_if_exists(self.env.cr, 'youth_analytics')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW youth_analytics AS (
                SELECT 
                    row_number() OVER () AS id,
                    'Youth Analytics' AS name,
                    CURRENT_DATE AS date,
                    NULL::INTEGER AS zone_id
            )
        """)

    def get_youth_statistics(self):
        """Get real-time youth statistics"""
        Youth = self.env['youth.youth']
        domain = []
        
        if self.zone_id:
            domain.append(('zone_id', '=', self.zone_id.id))
            
        youth_records = Youth.search(domain)
        
        return {
            'total_youth': len(youth_records),
            'active_youth': len(youth_records.filtered(lambda y: y.status == 'active')),
            'male_youth': len(youth_records.filtered(lambda y: y.gender == 'male')),
            'female_youth': len(youth_records.filtered(lambda y: y.gender == 'female')),
        }

    def get_application_statistics(self):
        """Get real-time application statistics"""
        Application = self.env['youth.application']
        domain = []
        
        if self.zone_id:
            domain.append(('applicant_zone', '=', self.zone_id.id))
        if self.date_from:
            domain.append(('application_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('application_date', '<=', self.date_to))
            
        applications = Application.search(domain)
        
        total = len(applications)
        approved = len(applications.filtered(lambda a: a.status == 'approved'))
        
        return {
            'total_applications': total,
            'approved_applications': approved,
            'application_success_rate': (approved / total * 100) if total > 0 else 0.0,
            'cdf_applications': len(applications.filtered(lambda a: a.application_type == 'cdf')),
        }

    def get_program_statistics(self):
        """Get real-time program statistics"""
        Program = self.env['youth.program']
        domain = []
        
        if self.zone_id:
            domain.append(('zone_id', '=', self.zone_id.id))
            
        programs = Program.search(domain)
        
        return {
            'total_programs': len(programs),
            'active_programs': len(programs.filtered(lambda p: p.status == 'active')),
            'completed_programs': len(programs.filtered(lambda p: p.status == 'completed')),
        }

    def action_refresh_data(self):
        """Refresh dashboard data"""
        # Update statistics
        youth_stats = self.get_youth_statistics()
        app_stats = self.get_application_statistics()
        prog_stats = self.get_program_statistics()
        
        # Update current record with fresh data
        self.write({
            **youth_stats,
            **app_stats,
            **prog_stats,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_view_youth_by_zone(self):
        """View youth by zone"""
        return {
            'name': 'Youth by Zone',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,list,form',
            'domain': [('zone_id', '=', self.zone_id.id)] if self.zone_id else [],
            'context': {'group_by': 'zone_id'},
            'target': 'current',
        }

    def action_view_applications_by_status(self):
        """View applications by status"""
        return {
            'name': 'Applications by Status',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.application',
            'view_mode': 'list,form',
            'context': {'group_by': 'status'},
            'target': 'current',
        }

    def action_view_programs_by_type(self):
        """View programs by type"""
        return {
            'name': 'Programs by Type',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.program',
            'view_mode': 'kanban,list,form',
            'context': {'group_by': 'program_type'},
            'target': 'current',
        }


class YouthDashboard(models.TransientModel):
    _name = 'youth.dashboard'
    _description = 'Youth Dashboard Wizard'

    zone_id = fields.Many2one('youth.zone', string='Filter by Zone')
    date_from = fields.Date(string='Date From', default=fields.Date.context_today)
    date_to = fields.Date(string='Date To', default=fields.Date.context_today)
    
    def action_generate_dashboard(self):
        """Generate dashboard with filters"""
        return {
            'name': 'Youth Analytics Dashboard',
            'type': 'ir.actions.act_window',
            'res_model': 'youth.analytics',
            'view_mode': 'form',
            'context': {
                'default_zone_id': self.zone_id.id if self.zone_id else False,
                'default_date_from': self.date_from,
                'default_date_to': self.date_to,
            },
            'target': 'current',
        }