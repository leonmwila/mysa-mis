from odoo import models, fields


class CommonAssociationYouthExtension(models.Model):
    _inherit = 'common.association'

    youth_zone_id = fields.Many2one(
        'youth.zone',
        string='Youth Zone',
        compute='_compute_youth_zone_id',
        inverse='_inverse_youth_zone_id',
        store=False,
    )
    youth_member_ids = fields.Many2many(
        'youth.youth',
        string='Youth Members',
        compute='_compute_youth_member_ids',
        inverse='_inverse_youth_member_ids',
        store=False,
    )

    def _compute_youth_zone_id(self):
        Zone = self.env['youth.zone']
        for record in self:
            association_id = record.id if isinstance(record.id, int) else record._origin.id
            if not association_id:
                record.youth_zone_id = False
                continue
            zone = Zone.search([('common_association_ids', 'in', [association_id])], limit=1)
            record.youth_zone_id = zone

    def _inverse_youth_zone_id(self):
        Zone = self.env['youth.zone']
        for record in self:
            association_id = record.id if isinstance(record.id, int) else record._origin.id
            if not association_id:
                continue
            linked_zones = Zone.search([('common_association_ids', 'in', [association_id])])
            if linked_zones:
                for zone in linked_zones:
                    zone.common_association_ids = [(3, association_id)]
            if record.youth_zone_id:
                record.youth_zone_id.common_association_ids = [(4, association_id)]

    def _compute_youth_member_ids(self):
        Youth = self.env['youth.youth']
        for record in self:
            association_id = record.id if isinstance(record.id, int) else record._origin.id
            if not association_id:
                record.youth_member_ids = [(5, 0, 0)]
                continue
            record.youth_member_ids = Youth.search([('common_association_ids', 'in', [association_id])])

    def _inverse_youth_member_ids(self):
        Youth = self.env['youth.youth']
        for record in self:
            association_id = record.id if isinstance(record.id, int) else record._origin.id
            if not association_id:
                continue
            current_members = Youth.search([('common_association_ids', 'in', [association_id])])
            selected_members = record.youth_member_ids

            to_add = selected_members - current_members
            to_remove = current_members - selected_members

            if to_add:
                to_add.write({'common_association_ids': [(4, association_id)]})
            if to_remove:
                to_remove.write({'common_association_ids': [(3, association_id)]})
