from odoo import models, fields, api

class EventProgram(models.Model):
    _name = 'event.program'
    _description = 'Event or Program'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('all','All')
    ], string='Gender', required=True, default='all')
    attended = fields.Integer(string='Number of Attendees')
    category = fields.Selection([
        ('youth', 'Youth Development'),
        ('arts', 'Arts & Culture'),
        ('sports', 'Sports')
    ], string='Category', required=True)
    age_group = fields.Selection([
        ('u10', 'Under 10'),
        ('u12', 'Under 12'),
        ('u14', 'Under 14'),
        ('u16', 'Under 16'),
        ('u18', 'Under 18'),
        ('u21', 'Under 21'),
        ('adult', 'Adult'),
        ('open', 'Open'),
    ], string='Age Group')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    location = fields.Char(string='Location')
    coordinator_id = fields.Many2one('res.users', string='Coordinator')
    # organizer_association_id = fields.Many2one('sports.association', string='Organizing Association')
    organizer_association_name = fields.Char(string='Organizing Association')
    participants_ids = fields.One2many('event.participant', 'program_id', string='Participants')
    
    # Athlete Participants - Many2many relationship
    athlete_participants_ids = fields.Many2many(
        'sports.athlete',
        string='Athlete Participants',
        help="Athletes participating in this event/program"
    )
    
    results_ids = fields.One2many('event.result', 'program_id', string='Results')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

    # @api.depends('athlete_participants_ids', 'participants_ids')
    # def _compute_participant_count(self):
    #     for record in self:
    #         record.participant_count = len(record.athlete_participants_ids) + len(record.participants_ids)

    @api.model
    def start_event(self):
        self.state = 'ongoing'

    @api.model
    def complete_event(self):
        self.state = 'completed'
