from odoo import models, fields, api

class SportsZone(models.Model):
    _name = 'sports.zone'
    _description = 'Sports Zone/Region Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Zone Name', required=True)
    code = fields.Char(string='Zone Code', required=True)
    province = fields.Char(string='Province')
    districts = fields.Text(string='Districts Covered')
    zone_coordinator_id = fields.Many2one('res.users', string='Zone Coordinator')
    
    # Statistics
    total_associations = fields.Integer(string='Total Associations', compute='_compute_statistics')
    total_athletes = fields.Integer(string='Total Athletes', compute='_compute_statistics')
    active_programs = fields.Integer(string='Active Programs', compute='_compute_statistics')
    
    # Relationships
    association_ids = fields.One2many('sports.association', 'zone_id', string='Associations')
    athlete_ids = fields.One2many('sports.athlete', 'zone_id', string='Athletes')
    
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('association_ids', 'athlete_ids')
    def _compute_statistics(self):
        for record in self:
            record.total_associations = len(record.association_ids)
            record.total_athletes = len(record.athlete_ids)
            # Active programs would need event integration
            record.active_programs = 0

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"
            result.append((record.id, name))
        return result

    def action_generate_zone_report(self):
        """Generate zone performance report"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Zone Report',
            'res_model': 'sports.analytics',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_zone_id': self.id,
                'default_sport_type': 'all',
            }
        }

    def action_view_associations(self):
        """View all associations in this zone"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Associations',
            'res_model': 'sports.association',
            'view_mode': 'list,form,kanban',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id}
        }

    def action_view_athletes(self):
        """View all athletes in this zone"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Athletes',
            'res_model': 'sports.athlete',
            'view_mode': 'kanban,list,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id}
        }

    def action_view_programs(self):
        """View all programs in this zone"""
        # For now, return a simple message since event integration is not active
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Programs',
                'message': 'Program management will be available when event integration is enabled.',
                'type': 'info'
            }
        }