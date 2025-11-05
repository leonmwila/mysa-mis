from odoo import models, fields

class EventResult(models.Model):
    _name = 'event.result'
    _description = 'Event or Program Result'

    program_id = fields.Many2one('event.program', string='Program/Event')
    participant_id = fields.Many2one('event.participant', string='Participant')
    score = fields.Float(string='Score')
    position = fields.Integer(string='Position')
    remarks = fields.Text(string='Remarks')
