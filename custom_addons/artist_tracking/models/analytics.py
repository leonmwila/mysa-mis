from odoo import models, fields, api
from datetime import datetime, timedelta


class ArtistAnalytics(models.Model):
    _name = 'artist.analytics'
    _description = 'Artist Analytics and Insights'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char('Analytics Report Name')
    artist_id = fields.Many2one('artist.artist', string='Artist')
    zone_id = fields.Many2one('artist.zone', string='Zone')
    association_id = fields.Many2one('artist.association', string='Association')
    
    # Time Period
    period_start = fields.Date('Period Start')
    period_end = fields.Date('Period End')
    
    # Performance Metrics
    total_performances = fields.Integer('Total Performances')
    avg_performance_rating = fields.Float('Average Performance Rating')
    total_audience_reached = fields.Integer('Total Audience Reached')
    
    # Achievement Metrics
    total_achievements = fields.Integer('Total Achievements')
    international_achievements = fields.Integer('International Achievements')
    national_achievements = fields.Integer('National Achievements')
    
    # Art Category
    art_category = fields.Selection([
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('mixed_media', 'Mixed Media'),
        ('other', 'Other')
    ], string='Art Category')
    
    # Financial Metrics
    total_earnings = fields.Float('Total Earnings')
    avg_performance_fee = fields.Float('Average Performance Fee')


class ArtistDashboard(models.TransientModel):
    _name = 'artist.dashboard'
    _description = 'Artist Dashboard Analytics'

    # Summary Statistics
    total_artists = fields.Integer('Total Artists', compute='_compute_summary_stats')
    active_artists = fields.Integer('Active Artists', compute='_compute_summary_stats')
    total_associations = fields.Integer('Total Associations', compute='_compute_summary_stats')
    total_performances_this_month = fields.Integer('Performances This Month', compute='_compute_summary_stats')
    
    # Art Category Distribution
    dance_artists = fields.Integer('Dance Artists', compute='_compute_category_distribution')
    music_artists = fields.Integer('Music Artists', compute='_compute_category_distribution')
    visual_arts_artists = fields.Integer('Visual Arts Artists', compute='_compute_category_distribution')
    theater_artists = fields.Integer('Theater Artists', compute='_compute_category_distribution')
    
    # Performance Analytics
    avg_performance_rating = fields.Float('Average Performance Rating', compute='_compute_performance_analytics')
    total_performances_ytd = fields.Integer('Total Performances YTD', compute='_compute_performance_analytics')
    top_performing_zone = fields.Char('Top Performing Zone', compute='_compute_performance_analytics')
    
    # Achievement Analytics
    total_achievements_ytd = fields.Integer('Total Achievements YTD', compute='_compute_achievement_analytics')
    international_achievements = fields.Integer('International Achievements', compute='_compute_achievement_analytics')
    most_awarded_category = fields.Char('Most Awarded Category', compute='_compute_achievement_analytics')

    @api.depends()
    def _compute_summary_stats(self):
        for record in self:
            # Total and active artists
            record.total_artists = self.env['artist.artist'].search_count([])
            record.active_artists = self.env['artist.artist'].search_count([('status', '=', 'active')])
            
            # Total associations
            record.total_associations = self.env['artist.association'].search_count([])
            
            # Performances this month
            start_of_month = datetime.now().replace(day=1).date()
            record.total_performances_this_month = self.env['artist.performance.metric'].search_count([
                ('performance_date', '>=', start_of_month),
                ('status', '=', 'completed')
            ])

    @api.depends()
    def _compute_category_distribution(self):
        for record in self:
            record.dance_artists = self.env['artist.artist'].search_count([('art_category', '=', 'dance')])
            record.music_artists = self.env['artist.artist'].search_count([('art_category', '=', 'music')])
            record.visual_arts_artists = self.env['artist.artist'].search_count([('art_category', '=', 'visual_arts')])
            record.theater_artists = self.env['artist.artist'].search_count([('art_category', '=', 'theater')])

    @api.depends()
    def _compute_performance_analytics(self):
        for record in self:
            # Average performance rating
            performances = self.env['artist.performance.metric'].search([('overall_rating', '>', 0)])
            if performances:
                record.avg_performance_rating = sum(performances.mapped('overall_rating')) / len(performances)
            else:
                record.avg_performance_rating = 0.0
            
            # Total performances year to date
            start_of_year = datetime.now().replace(month=1, day=1).date()
            record.total_performances_ytd = self.env['artist.performance.metric'].search_count([
                ('performance_date', '>=', start_of_year),
                ('status', '=', 'completed')
            ])
            
            # Top performing zone (placeholder - would need more complex query)
            record.top_performing_zone = 'Central Zone'  # This would be computed based on actual data

    @api.depends()
    def _compute_achievement_analytics(self):
        for record in self:
            # Total achievements year to date
            start_of_year = datetime.now().replace(month=1, day=1).date()
            record.total_achievements_ytd = self.env['artist.achievement'].search_count([
                ('achievement_date', '>=', start_of_year)
            ])
            
            # International achievements
            record.international_achievements = self.env['artist.achievement'].search_count([
                ('achievement_level', '=', 'international'),
                ('achievement_date', '>=', start_of_year)
            ])
            
            # Most awarded category (placeholder)
            record.most_awarded_category = 'Music'  # This would be computed based on actual data

    def action_view_artist_reports(self):
        """Open artist reports view"""
        return {
            'name': 'Artist Reports',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.report',
            'view_mode': 'tree,form,graph,pivot',
            'target': 'current',
        }

    def action_view_performance_analytics(self):
        """Open performance analytics view"""
        return {
            'name': 'Performance Analytics',
            'type': 'ir.actions.act_window',
            'res_model': 'artist.performance.metric',
            'view_mode': 'graph,pivot,tree',
            'target': 'current',
        }