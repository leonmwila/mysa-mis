from odoo import models, fields, api

class SportsAchievementIntegration(models.Model):
    _inherit = 'sports.achievement'
    
    # Event/Program Selection - dropdown of available programs
    event_program_id = fields.Many2one(
        'event.program', 
        string='Event/Program',
        help="Select the event/program this achievement was earned in",
        ondelete='set null'
    )
    
    @api.depends('event_program_id')
    def _compute_event_details(self):
        """Auto-populate event details when an event/program is selected"""
        for record in self:
            if record.event_program_id:
                record.event_name = record.event_program_id.name
                record.event_date_start = record.event_program_id.start_date
                record.event_date_end = record.event_program_id.end_date