from odoo import models, fields, api


class ArtistAchievementIntegration(models.Model):
    """
    Extension of artist.achievement to integrate with event_program_management module
    This allows achievements to be linked to specific events/programs
    """
    _inherit = 'artist.achievement'

    # Integration with Event Management Module
    event_program_id = fields.Many2one(
        'event.program', 
        string='Related Event/Program',
        help='Link this achievement to a specific event or program from the event management system'
    )
    
    # Additional fields for event-based achievements
    event_category = fields.Selection(
        related='event_program_id.category',
        string='Event Category',
        store=True,
        readonly=True
    )
    
    event_location = fields.Char(
        related='event_program_id.location',
        string='Event Location',
        store=True,
        readonly=True
    )
    
    event_start_date = fields.Date(
        related='event_program_id.start_date',
        string='Event Start Date',
        store=True,
        readonly=True
    )
    
    event_end_date = fields.Date(
        related='event_program_id.end_date',
        string='Event End Date',
        store=True,
        readonly=True
    )

    @api.onchange('event_program_id')
    def _onchange_event_program_id(self):
        """Auto-populate fields when an event/program is selected"""
        if self.event_program_id:
            # Auto-populate the event/competition name if not already filled
            if not self.event_competition_name:
                self.event_competition_name = self.event_program_id.name
            
            # Auto-populate location if not already filled
            if not self.location and self.event_program_id.location:
                self.location = self.event_program_id.location
                
            # Auto-populate achievement date with event start date if not filled
            if not self.achievement_date and self.event_program_id.start_date:
                self.achievement_date = self.event_program_id.start_date


class EventProgramArtistIntegration(models.Model):
    """
    Extension of event.program to add artist-specific features
    """
    _inherit = 'event.program'

    # Artist participants for arts events
    artist_participants_ids = fields.Many2many(
        'artist.artist',
        'event_program_artist_participants_rel',
        'event_program_id',
        'artist_id',
        string='Artist Participants',
        help='Artists participating in this event/program'
    )
    
    artist_participant_count = fields.Integer(
        'Number of Artist Participants',
        compute='_compute_artist_participant_count',
        store=True
    )
    
    # Arts-specific event information
    artistic_category = fields.Selection([
        ('dance', 'Dance Event'),
        ('music', 'Music Event'),
        ('visual_arts', 'Visual Arts Event'),
        ('theater', 'Theater Event'),
        ('film', 'Film Event'),
        ('literature', 'Literature Event'),
        ('digital_arts', 'Digital Arts Event'),
        ('mixed_arts', 'Mixed Arts Event'),
        ('cultural_festival', 'Cultural Festival'),
        ('other', 'Other')
    ], string='Artistic Category')
    
    # Event type for arts
    is_competition = fields.Boolean('Is Competition', default=False)
    is_exhibition = fields.Boolean('Is Exhibition', default=False)
    is_festival = fields.Boolean('Is Festival', default=False)
    is_workshop = fields.Boolean('Is Workshop/Training', default=False)
    
    # Jury and judging
    has_jury = fields.Boolean('Has Jury/Judges', default=False)
    jury_members = fields.Text('Jury Members')
    judging_criteria = fields.Text('Judging Criteria')
    
    # Related achievements
    artist_achievement_ids = fields.One2many(
        'artist.achievement',
        'event_program_id',
        string='Artist Achievements',
        help='Achievements earned in this event/program'
    )

    @api.depends('artist_participants_ids')
    def _compute_artist_participant_count(self):
        for record in self:
            record.artist_participant_count = len(record.artist_participants_ids)

    def action_view_artist_participants(self):
        """Action to view artist participants"""
        return {
            'name': f'Artist Participants - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.artist',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.artist_participants_ids.ids)],
            'context': {'default_event_participants_ids': [(6, 0, self.artist_participants_ids.ids)]}
        }

    def action_view_achievements(self):
        """Action to view achievements from this event"""
        return {
            'name': f'Achievements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.achievement',
            'view_mode': 'tree,form',
            'domain': [('event_program_id', '=', self.id)],
            'context': {'default_event_program_id': self.id}
        }