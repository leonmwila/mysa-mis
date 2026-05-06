from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class YouthDashboard(models.TransientModel):
    _name = 'youth.dashboard'
    _description = 'Youth Tracking Dashboard'

    name = fields.Char('Dashboard Name', default='Youth Analytics Dashboard')
    
    # Date filters
    date_from = fields.Date('Date From', default=lambda self: fields.Date.today() - relativedelta(months=6))
    date_to = fields.Date('Date To', default=fields.Date.today)
    
    # KPI - Youth Statistics
    total_youth = fields.Integer('Total Youth', compute='_compute_kpis')
    active_youth = fields.Integer('Active Youth', compute='_compute_kpis')
    inactive_youth = fields.Integer('Inactive Youth', compute='_compute_kpis')
    new_youth_this_month = fields.Integer('New This Month', compute='_compute_kpis')
    
    # KPI - Age Demographics
    youth_18_25 = fields.Integer('Youth 18-25', compute='_compute_demographics')
    youth_26_30 = fields.Integer('Youth 26-30', compute='_compute_demographics')
    youth_31_35 = fields.Integer('Youth 31-35', compute='_compute_demographics')
    
    # KPI - Gender Distribution
    male_youth = fields.Integer('Male Youth', compute='_compute_demographics')
    female_youth = fields.Integer('Female Youth', compute='_compute_demographics')
    
    # KPI - Education Levels
    primary_education = fields.Integer('Primary', compute='_compute_education')
    secondary_education = fields.Integer('Secondary', compute='_compute_education')
    tertiary_education = fields.Integer('Tertiary', compute='_compute_education')
    university_education = fields.Integer('University', compute='_compute_education')
    vocational_education = fields.Integer('Vocational', compute='_compute_education')
    
    # KPI - Employment Status
    employed_youth = fields.Integer('Employed', compute='_compute_employment')
    unemployed_youth = fields.Integer('Unemployed', compute='_compute_employment')
    student_youth = fields.Integer('Students', compute='_compute_employment')
    self_employed_youth = fields.Integer('Self-Employed', compute='_compute_employment')
    
    # KPI - Programs
    total_programs = fields.Integer('Total Programs', compute='_compute_programs')
    active_programs = fields.Integer('Active Programs', compute='_compute_programs')
    completed_programs = fields.Integer('Completed', compute='_compute_programs')
    total_participants = fields.Integer('Total Participants', compute='_compute_programs')
    
    # KPI - Applications
    total_applications = fields.Integer('Total Applications', compute='_compute_applications')
    pending_applications = fields.Integer('Pending', compute='_compute_applications')
    approved_applications = fields.Integer('Approved', compute='_compute_applications')
    rejected_applications = fields.Integer('Rejected', compute='_compute_applications')
    success_rate = fields.Float('Success Rate %', compute='_compute_applications')
    
    # KPI - CDF Statistics
    cdf_applications = fields.Integer('CDF Applications', compute='_compute_cdf')
    cdf_approved = fields.Integer('CDF Approved', compute='_compute_cdf')
    cdf_total_amount = fields.Float('Total CDF Amount', compute='_compute_cdf')
    cdf_average_amount = fields.Float('Avg CDF Amount', compute='_compute_cdf')
    
    # KPI - Organizations
    total_organizations = fields.Integer('Total Organizations', compute='_compute_organizations')
    active_organizations = fields.Integer('Active', compute='_compute_organizations')
    total_zones = fields.Integer('Total Zones', compute='_compute_organizations')
    
    @api.depends('date_from', 'date_to')
    def _compute_kpis(self):
        for record in self:
            Youth = self.env['youth.youth']
            
            all_youth = Youth.search([])
            record.total_youth = len(all_youth)
            record.active_youth = len(all_youth.filtered(lambda y: y.status == 'active'))
            record.inactive_youth = len(all_youth.filtered(lambda y: y.status == 'inactive'))
            
            # New youth this month
            start_of_month = fields.Date.today().replace(day=1)
            new_youth = Youth.search([
                ('registration_date', '>=', start_of_month),
                ('registration_date', '<=', fields.Date.today())
            ])
            record.new_youth_this_month = len(new_youth)
    
    @api.depends('date_from', 'date_to')
    def _compute_demographics(self):
        for record in self:
            Youth = self.env['youth.youth']
            all_youth = Youth.search([])
            
            # Age groups
            record.youth_18_25 = len(all_youth.filtered(lambda y: 18 <= y.age <= 25))
            record.youth_26_30 = len(all_youth.filtered(lambda y: 26 <= y.age <= 30))
            record.youth_31_35 = len(all_youth.filtered(lambda y: 31 <= y.age <= 35))
            
            # Gender
            record.male_youth = len(all_youth.filtered(lambda y: y.gender == 'male'))
            record.female_youth = len(all_youth.filtered(lambda y: y.gender == 'female'))
    
    @api.depends('date_from', 'date_to')
    def _compute_education(self):
        for record in self:
            Youth = self.env['youth.youth']
            all_youth = Youth.search([])
            
            record.primary_education = len(all_youth.filtered(lambda y: y.education_level == 'primary'))
            record.secondary_education = len(all_youth.filtered(lambda y: y.education_level == 'secondary'))
            record.tertiary_education = len(all_youth.filtered(lambda y: y.education_level == 'tertiary'))
            record.university_education = len(all_youth.filtered(lambda y: y.education_level == 'university'))
            record.vocational_education = len(all_youth.filtered(lambda y: y.education_level == 'vocational'))
    
    @api.depends('date_from', 'date_to')
    def _compute_employment(self):
        for record in self:
            Youth = self.env['youth.youth']
            all_youth = Youth.search([])
            
            record.employed_youth = len(all_youth.filtered(lambda y: y.employment_status == 'employed'))
            record.unemployed_youth = len(all_youth.filtered(lambda y: y.employment_status == 'unemployed'))
            record.student_youth = len(all_youth.filtered(lambda y: y.employment_status == 'student'))
            record.self_employed_youth = len(all_youth.filtered(lambda y: y.employment_status == 'self_employed'))
    
    @api.depends('date_from', 'date_to')
    def _compute_programs(self):
        for record in self:
            Program = self.env['youth.program']
            
            all_programs = Program.search([])
            record.total_programs = len(all_programs)
            record.active_programs = len(all_programs.filtered(lambda p: p.status == 'active'))
            record.completed_programs = len(all_programs.filtered(lambda p: p.status == 'completed'))
            
            # Total participants across all programs
            total_participants = sum(program.current_participants for program in all_programs)
            record.total_participants = total_participants
    
    @api.depends('date_from', 'date_to')
    def _compute_applications(self):
        for record in self:
            Application = self.env['youth.application']
            
            all_applications = Application.search([])
            record.total_applications = len(all_applications)
            record.pending_applications = len(all_applications.filtered(lambda a: a.status == 'submitted'))
            record.approved_applications = len(all_applications.filtered(lambda a: a.status == 'approved'))
            record.rejected_applications = len(all_applications.filtered(lambda a: a.status == 'rejected'))
            
            # Success rate
            if record.total_applications > 0:
                record.success_rate = (record.approved_applications / record.total_applications) * 100
            else:
                record.success_rate = 0.0
    
    @api.depends('date_from', 'date_to')
    def _compute_cdf(self):
        for record in self:
            Application = self.env['youth.application']
            
            cdf_apps = Application.search([('application_type', '=', 'cdf')])
            record.cdf_applications = len(cdf_apps)
            record.cdf_approved = len(cdf_apps.filtered(lambda a: a.status == 'approved'))
            
            approved_cdf = cdf_apps.filtered(lambda a: a.status == 'approved')
            record.cdf_total_amount = sum(app.amount_requested for app in approved_cdf)
            
            if record.cdf_approved > 0:
                record.cdf_average_amount = record.cdf_total_amount / record.cdf_approved
            else:
                record.cdf_average_amount = 0.0
    
    @api.depends('date_from', 'date_to')
    def _compute_organizations(self):
        for record in self:
            Organization = self.env['common.association']
            Zone = self.env['youth.zone']
            
            all_orgs = Organization.search([('is_youth', '=', True)])
            record.total_organizations = len(all_orgs)
            record.active_organizations = len(all_orgs.filtered(lambda o: o.active == True))
            record.total_zones = Zone.search_count([])
    
    def action_view_youth(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Youth',
            'res_model': 'youth.youth',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
    
    def action_view_programs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Programs',
            'res_model': 'youth.program',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
    
    def action_view_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Applications',
            'res_model': 'youth.application',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_open_dashboard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Youth Dashboard',
            'res_model': 'youth.dashboard',
            'view_mode': 'form',
            'target': 'current',
        }
