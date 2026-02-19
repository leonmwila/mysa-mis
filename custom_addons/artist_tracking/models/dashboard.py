from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ArtistDashboard(models.TransientModel):
    _name = 'artist.dashboard'
    _description = 'Artist Tracking Dashboard'

    name = fields.Char('Dashboard Name', default='Artist Analytics Dashboard')
    
    # Date filters
    date_from = fields.Date('Date From', default=lambda self: fields.Date.today() - relativedelta(months=6))
    date_to = fields.Date('Date To', default=fields.Date.today)
    
    # KPI - Summary Statistics
    total_artists = fields.Integer('Total Artists', compute='_compute_kpis')
    active_artists = fields.Integer('Active Artists', compute='_compute_kpis')
    inactive_artists = fields.Integer('Inactive Artists', compute='_compute_kpis')
    new_artists_this_month = fields.Integer('New Artists This Month', compute='_compute_kpis')
    professional_artists = fields.Integer('Professional Artists', compute='_compute_kpis')
    
    # KPI - Performance Metrics
    total_performances = fields.Integer('Total Performances', compute='_compute_performance_kpis')
    performances_this_month = fields.Integer('Performances This Month', compute='_compute_performance_kpis')
    avg_performance_rating = fields.Float('Avg Performance Rating', compute='_compute_performance_kpis')
    total_audience_reached = fields.Integer('Total Audience Reached', compute='_compute_performance_kpis')
    upcoming_performances = fields.Integer('Upcoming Performances', compute='_compute_performance_kpis')
    
    # KPI - Achievement Metrics
    total_achievements = fields.Integer('Total Achievements', compute='_compute_achievement_kpis')
    achievements_this_month = fields.Integer('Achievements This Month', compute='_compute_achievement_kpis')
    international_achievements = fields.Integer('International Achievements', compute='_compute_achievement_kpis')
    national_achievements = fields.Integer('National Achievements', compute='_compute_achievement_kpis')
    awards_won = fields.Integer('Awards Won', compute='_compute_achievement_kpis')
    
    # KPI - Association & Zone Metrics
    total_associations = fields.Integer('Total Associations', compute='_compute_association_kpis')
    total_zones = fields.Integer('Total Zones', compute='_compute_association_kpis')
    artists_with_association = fields.Integer('Artists with Association', compute='_compute_association_kpis')
    avg_artists_per_zone = fields.Float('Avg Artists per Zone', compute='_compute_association_kpis')
    
    # Art Category Distribution
    dance_artists_count = fields.Integer('Dance Artists', compute='_compute_category_distribution')
    music_artists_count = fields.Integer('Music Artists', compute='_compute_category_distribution')
    visual_arts_count = fields.Integer('Visual Arts', compute='_compute_category_distribution')
    theater_artists_count = fields.Integer('Theater Artists', compute='_compute_category_distribution')
    film_artists_count = fields.Integer('Film Artists', compute='_compute_category_distribution')
    literature_artists_count = fields.Integer('Literature Artists', compute='_compute_category_distribution')
    digital_arts_count = fields.Integer('Digital Arts', compute='_compute_category_distribution')
    other_arts_count = fields.Integer('Other Arts', compute='_compute_category_distribution')
    
    # Skill Level Distribution
    beginner_count = fields.Integer('Beginners', compute='_compute_skill_distribution')
    intermediate_count = fields.Integer('Intermediate', compute='_compute_skill_distribution')
    advanced_count = fields.Integer('Advanced', compute='_compute_skill_distribution')
    professional_count = fields.Integer('Professional', compute='_compute_skill_distribution')
    master_count = fields.Integer('Masters', compute='_compute_skill_distribution')
    
    # Gender Distribution
    male_artists = fields.Integer('Male Artists', compute='_compute_gender_distribution')
    female_artists = fields.Integer('Female Artists', compute='_compute_gender_distribution')
    
    # Top Performers
    top_artist_name = fields.Char('Top Performing Artist', compute='_compute_top_performers')
    top_artist_performances = fields.Integer('Top Artist Performances', compute='_compute_top_performers')
    most_awarded_artist = fields.Char('Most Awarded Artist', compute='_compute_top_performers')
    most_awarded_count = fields.Integer('Most Awards Count', compute='_compute_top_performers')
    
    @api.depends()
    def _compute_kpis(self):
        for record in self:
            Artist = self.env['artist.artist']
            
            # Total counts
            record.total_artists = Artist.search_count([])
            record.active_artists = Artist.search_count([('status', '=', 'active')])
            record.inactive_artists = Artist.search_count([('status', 'in', ['inactive', 'suspended', 'retired'])])
            record.professional_artists = Artist.search_count([('is_professional', '=', True)])
            
            # New artists this month
            start_of_month = datetime.now().replace(day=1).date()
            record.new_artists_this_month = Artist.search_count([
                ('registration_date', '>=', start_of_month)
            ])
    
    @api.depends()
    def _compute_performance_kpis(self):
        for record in self:
            Performance = self.env['artist.performance.metric']
            
            # Total performances
            record.total_performances = Performance.search_count([])
            
            # Performances this month
            start_of_month = datetime.now().replace(day=1).date()
            record.performances_this_month = Performance.search_count([
                ('performance_date', '>=', start_of_month),
                ('performance_date', '<=', fields.Date.today())
            ])
            
            # Upcoming performances
            record.upcoming_performances = Performance.search_count([
                ('performance_date', '>', fields.Date.today())
            ])
            
            # Average rating
            performances = Performance.search([('overall_rating', '>', 0)])
            if performances:
                record.avg_performance_rating = sum(performances.mapped('overall_rating')) / len(performances)
            else:
                record.avg_performance_rating = 0.0
            
            # Total audience reached
            record.total_audience_reached = sum(Performance.search([]).mapped('actual_audience'))
    
    @api.depends()
    def _compute_achievement_kpis(self):
        for record in self:
            Achievement = self.env['artist.achievement']
            
            # Total achievements
            record.total_achievements = Achievement.search_count([])
            
            # Achievements this month
            start_of_month = datetime.now().replace(day=1).date()
            record.achievements_this_month = Achievement.search_count([
                ('achievement_date', '>=', start_of_month)
            ])
            
            # By level
            record.international_achievements = Achievement.search_count([
                ('achievement_level', '=', 'international')
            ])
            record.national_achievements = Achievement.search_count([
                ('achievement_level', '=', 'national')
            ])
            
            # Awards won
            record.awards_won = Achievement.search_count([
                ('achievement_type', '=', 'award')
            ])
    
    @api.depends()
    def _compute_association_kpis(self):
        for record in self:
            Association = self.env['common.association']
            Zone = self.env['artist.zone']
            Artist = self.env['artist.artist']
            
            record.total_associations = Association.search_count([('is_arts', '=', True)])
            record.total_zones = Zone.search_count([])
            record.artists_with_association = Artist.search_count([
                ('common_association_ids', '!=', False)
            ])
            
            # Average artists per zone
            zones = Zone.search([])
            if zones:
                total_artists_in_zones = sum(zone.artist_count for zone in zones)
                record.avg_artists_per_zone = total_artists_in_zones / len(zones) if len(zones) > 0 else 0
            else:
                record.avg_artists_per_zone = 0.0
    
    @api.depends()
    def _compute_category_distribution(self):
        for record in self:
            Artist = self.env['artist.artist']
            
            record.dance_artists_count = Artist.search_count([('art_category', '=', 'dance')])
            record.music_artists_count = Artist.search_count([('art_category', '=', 'music')])
            record.visual_arts_count = Artist.search_count([('art_category', '=', 'visual_arts')])
            record.theater_artists_count = Artist.search_count([('art_category', '=', 'theater')])
            record.film_artists_count = Artist.search_count([('art_category', '=', 'film')])
            record.literature_artists_count = Artist.search_count([('art_category', '=', 'literature')])
            record.digital_arts_count = Artist.search_count([('art_category', '=', 'digital_arts')])
            record.other_arts_count = Artist.search_count([('art_category', '=', 'other')])
    
    @api.depends()
    def _compute_skill_distribution(self):
        for record in self:
            Artist = self.env['artist.artist']
            
            record.beginner_count = Artist.search_count([('skill_level', '=', 'beginner')])
            record.intermediate_count = Artist.search_count([('skill_level', '=', 'intermediate')])
            record.advanced_count = Artist.search_count([('skill_level', '=', 'advanced')])
            record.professional_count = Artist.search_count([('skill_level', '=', 'professional')])
            record.master_count = Artist.search_count([('skill_level', '=', 'master')])
    
    @api.depends()
    def _compute_gender_distribution(self):
        for record in self:
            Artist = self.env['artist.artist']
            
            record.male_artists = Artist.search_count([('gender', '=', 'male')])
            record.female_artists = Artist.search_count([('gender', '=', 'female')])
    
    @api.depends()
    def _compute_top_performers(self):
        for record in self:
            # Top performing artist (most performances)
            artist_performances = self.env['artist.performance.metric'].read_group(
                [('status', '=', 'completed')],
                ['artist_id'],
                ['artist_id']
            )
            
            if artist_performances:
                top_performer = max(artist_performances, key=lambda x: x['artist_id_count'])
                artist = self.env['artist.artist'].browse(top_performer['artist_id'][0])
                record.top_artist_name = artist.name
                record.top_artist_performances = top_performer['artist_id_count']
            else:
                record.top_artist_name = 'N/A'
                record.top_artist_performances = 0
            
            # Most awarded artist
            artist_achievements = self.env['artist.achievement'].read_group(
                [],
                ['artist_id'],
                ['artist_id']
            )
            
            if artist_achievements:
                most_awarded = max(artist_achievements, key=lambda x: x['artist_id_count'])
                artist = self.env['artist.artist'].browse(most_awarded['artist_id'][0])
                record.most_awarded_artist = artist.name
                record.most_awarded_count = most_awarded['artist_id_count']
            else:
                record.most_awarded_artist = 'N/A'
                record.most_awarded_count = 0
    
    def action_view_artists(self):
        """Open artists list view"""
        return {
            'name': 'Artists',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.artist',
            'view_mode': 'kanban,tree,form',
            'domain': [],
            'context': {'create': True},
        }
    
    def action_view_performances(self):
        """Open performances list view"""
        return {
            'name': 'Performances',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.performance.metric',
            'view_mode': 'tree,form,calendar,graph',
            'domain': [],
            'context': {'create': True},
        }
    
    def action_view_achievements(self):
        """Open achievements list view"""
        return {
            'name': 'Achievements',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.achievement',
            'view_mode': 'tree,form,graph',
            'domain': [],
            'context': {'create': True},
        }
    
    def action_open_dashboard(self):
        """Open the dashboard form view"""
        return {
            'name': 'Artist Dashboard',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

