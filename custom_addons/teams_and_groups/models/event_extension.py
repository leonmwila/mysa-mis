from odoo import models, fields, api


class EventProgramExtension(models.Model):
    _inherit = 'event.program'
    
    # Team Participants
    team_participants_ids = fields.Many2many(
        'sports.team',
        'sports_team_event_rel',
        'event_id',
        'team_id',
        string='Team Participants',
        help="Sports teams participating in this event/program"
    )
    
    # Band Participants
    band_participants_ids = fields.Many2many(
        'artist.band',
        'artist_band_event_rel',
        'event_id',
        'band_id',
        string='Band/Group Participants',
        help="Artist bands/groups participating in this event/program"
    )

    def write(self, vals):
        """Override write to automatically add team/band members to participants when teams/bands are added"""
        result = super().write(vals)
        
        # Check if team_participants_ids or band_participants_ids were modified
        if 'team_participants_ids' in vals or 'band_participants_ids' in vals:
            for record in self:
                # Get all athletes from all teams in this event/program
                team_members = self.env['sports.athlete']
                for team in record.team_participants_ids:
                    team_members |= team.member_ids
                
                # Add team members to athlete_participants_ids (union, so existing athletes remain)
                if team_members:
                    record.athlete_participants_ids = record.athlete_participants_ids | team_members
                
                # Get all artists from all bands in this event/program (if artist_participants_ids exists)
                if hasattr(record, 'artist_participants_ids'):
                    band_members = self.env['artist.artist']
                    for band in record.band_participants_ids:
                        band_members |= band.member_ids
                    
                    # Add band members to artist_participants_ids (union, so existing artists remain)
                    if band_members:
                        record.artist_participants_ids = record.artist_participants_ids | band_members
        
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically add team/band members to participants"""
        records = super().create(vals_list)
        
        # After creation, sync team/band members to participants
        for record in records:
            if record.team_participants_ids:
                team_members = self.env['sports.athlete']
                for team in record.team_participants_ids:
                    team_members |= team.member_ids
                
                if team_members:
                    record.athlete_participants_ids = record.athlete_participants_ids | team_members
            
            # Sync band members to artist participants (if artist_participants_ids exists)
            if hasattr(record, 'artist_participants_ids') and record.band_participants_ids:
                band_members = self.env['artist.artist']
                for band in record.band_participants_ids:
                    band_members |= band.member_ids
                
                if band_members:
                    record.artist_participants_ids = record.artist_participants_ids | band_members
        
        return records

