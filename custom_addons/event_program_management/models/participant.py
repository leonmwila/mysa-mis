from odoo import models, fields, api

class EventParticipant(models.Model):
    _name = 'event.participant'
    _description = 'Event Participant'

    name = fields.Char(string='Full Name', required=True)
    # athlete_id = fields.Many2one('sports.athlete', string='Athlete', 
    #                             help="Select an athlete from the sports registry")
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    program_id = fields.Many2one('event.program', string='Program/Event')
    contact = fields.Char(string='Contact')
    address = fields.Text(string='Address')
    province = fields.Char(string='Province')
    attended = fields.Boolean(string='Attended', default=False)
