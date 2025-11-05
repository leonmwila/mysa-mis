from odoo import models, fields, api

class UserProfile(models.Model):
    _name = 'user.profile'
    _description = 'User Profile for Ministry Staff'

    user_id = fields.Many2one('res.users', string='System User', required=True)
    national_id = fields.Char(string='National ID')
    phone = fields.Char(string='Phone Number')
    department = fields.Char(string='Department')
    council = fields.Char(string='Council')
    role = fields.Selection([
        ('admin', 'Administrator'),
        ('minister', 'Minister'),
        ('director', 'Director'),
        ('chief', 'Chief'),
        ('officer', 'Officer'),
        ('registry', 'Registry Staff'),
        ('auditor', 'Auditor'),
        ('support', 'External Support Staff')
    ], string='Role')
    achievements = fields.Text(string='Achievements')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='active')

    @api.depends('role')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} ({record.role})" if record.user_id else record.role
