from odoo import models, fields, api
from datetime import datetime, timedelta

class SportsAnalytics(models.TransientModel):
    _name = 'sports.analytics'
    _description = 'Sports Analytics and Reporting'

    # Filter Parameters
    date_from = fields.Date(string='From Date', default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='To Date', default=fields.Date.today)
    sport_type = fields.Selection([
        ('all', 'All Sports'),
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('athletics', 'Athletics'),
        ('swimming', 'Swimming'),
        ('boxing', 'Boxing'),
        ('tennis', 'Tennis'),
        ('netball', 'Netball'),
        ('cricket', 'Cricket'),
        ('rugby', 'Rugby'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('badminton', 'Badminton'),
        ('other', 'Other')
    ], string='Sport Type', default='all')
    
    zone_id = fields.Many2one('sports.zone', string='Zone')
    association_id = fields.Many2one('sports.association', string='Association')
    
    # Computed Analytics
    total_athletes = fields.Integer(string='Total Athletes', compute='_compute_analytics')
    active_athletes = fields.Integer(string='Active Athletes', compute='_compute_analytics')
    total_associations = fields.Integer(string='Total Associations', compute='_compute_analytics')
    total_achievements = fields.Integer(string='Total Achievements', compute='_compute_analytics')
    total_events = fields.Integer(string='Total Events', compute='_compute_analytics')
    
    # Medal Statistics
    gold_medals = fields.Integer(string='Gold Medals', compute='_compute_analytics')
    silver_medals = fields.Integer(string='Silver Medals', compute='_compute_analytics')
    bronze_medals = fields.Integer(string='Bronze Medals', compute='_compute_analytics')
    
    # Performance Metrics
    avg_performance_improvement = fields.Float(string='Avg Performance Improvement (%)', compute='_compute_analytics')
    top_performing_zone = fields.Char(string='Top Performing Zone', compute='_compute_analytics')
    
    @api.depends('date_from', 'date_to', 'sport_type', 'zone_id', 'association_id')
    def _compute_analytics(self):
        for record in self:
            # Build domain for filtering
            athlete_domain = []
            achievement_domain = []
            association_domain = [('active', '=', True)]
            
            if record.sport_type and record.sport_type != 'all':
                athlete_domain.append(('primary_sport', '=', record.sport_type))
                association_domain.append(('sports_type', '=', record.sport_type))
            
            if record.zone_id:
                athlete_domain.append(('zone_id', '=', record.zone_id.id))
                association_domain.append(('zone_id', '=', record.zone_id.id))
            
            if record.association_id:
                athlete_domain.append(('association_id', '=', record.association_id.id))
            
            if record.date_from and record.date_to:
                achievement_domain.extend([
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to)
                ])
            
            # Get athletes
            athletes = self.env['sports.athlete'].search(athlete_domain)
            record.total_athletes = len(athletes)
            record.active_athletes = len(athletes.filtered(lambda x: x.athlete_status == 'active'))
            
            # Get associations
            associations = self.env['sports.association'].search(association_domain)
            record.total_associations = len(associations)
            
            # Get achievements
            if athletes:
                achievement_domain.append(('athlete_id', 'in', athletes.ids))
            achievements = self.env['sports.achievement'].search(achievement_domain)
            
            record.total_achievements = len(achievements)
            record.gold_medals = len(achievements.filtered(lambda x: x.medal_type == 'gold'))
            record.silver_medals = len(achievements.filtered(lambda x: x.medal_type == 'silver'))
            record.bronze_medals = len(achievements.filtered(lambda x: x.medal_type == 'bronze'))
            
            # Get events (from event_program_management module)
            event_domain = []
            if record.date_from and record.date_to:
                event_domain.extend([
                    ('start_date', '>=', record.date_from),
                    ('end_date', '<=', record.date_to)
                ])
            
            # Check if event.program model exists to avoid dependency issues
            if 'event.program' in self.env:
                events = self.env['event.program'].search(event_domain)
                record.total_events = len(events.filtered(lambda x: x.category == 'sports'))
            else:
                record.total_events = 0
            
            # Calculate performance improvement
            record.avg_performance_improvement = record._calculate_performance_improvement(athletes)
            
            # Find top performing zone
            record.top_performing_zone = record._get_top_performing_zone()

    def _calculate_performance_improvement(self, athletes):
        """Calculate average performance improvement"""
        if not athletes:
            return 0.0
        
        total_improvement = 0.0
        improvement_count = 0
        
        for athlete in athletes:
            # Get performance metrics with improvement data
            metrics = athlete.performance_metric_ids.filtered(lambda x: x.improvement != 0)
            if metrics:
                participant_avg = sum(metrics.mapped('improvement')) / len(metrics)
                total_improvement += participant_avg
                improvement_count += 1
        
        return (total_improvement / improvement_count) if improvement_count > 0 else 0.0

    def _get_top_performing_zone(self):
        """Get the zone with the most achievements"""
        zones = self.env['sports.zone'].search([])
        zone_scores = {}
        
        for zone in zones:
            athletes = self.env['sports.athlete'].search([('zone_id', '=', zone.id)])
            achievements = self.env['sports.achievement'].search([
                ('athlete_id', 'in', athletes.ids),
                ('verified', '=', True)
            ])
            
            # Calculate zone score (Gold=3, Silver=2, Bronze=1)
            score = 0
            for achievement in achievements:
                if achievement.medal_type == 'gold':
                    score += 3
                elif achievement.medal_type == 'silver':
                    score += 2
                elif achievement.medal_type == 'bronze':
                    score += 1
            
            zone_scores[zone.name] = score
        
        if zone_scores:
            return max(zone_scores, key=zone_scores.get)
        return ''

    def action_generate_report(self):
        """Generate detailed analytics report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'sports_tracking.sports_analytics_report',
            'model': 'sports.analytics',
            'report_type': 'qweb-pdf',
            'data': {
                'ids': self.ids,
                'model': 'sports.analytics'
            },
            'context': self.env.context,
        }

    def action_export_data(self):
        """Export analytics data to Excel/CSV"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Export Data',
                'message': 'Analytics data export functionality coming soon. Use the Generate Report button for PDF reports.',
                'type': 'info'
            }
        }

    def get_participation_by_zone(self):
        """Get participation statistics by zone"""
        zones = self.env['sports.zone'].search([])
        zone_data = []
        
        for zone in zones:
            athletes = self.env['sports.athlete'].search([('zone_id', '=', zone.id)])
            if self.sport_type and self.sport_type != 'all':
                athletes = athletes.filtered(lambda x: x.primary_sport == self.sport_type)
            
            zone_data.append({
                'zone_name': zone.name,
                'total_athletes': len(athletes),
                'active_athletes': len(athletes.filtered(lambda x: x.athlete_status == 'active')),
                'associations': len(zone.association_ids),
                'achievements': len(self.env['sports.achievement'].search([
                    ('athlete_id', 'in', athletes.ids),
                    ('verified', '=', True)
                ]))
            })
        
        return zone_data

    def get_performance_trends(self):
        """Get performance trends over time"""
        domain = []
        if self.date_from and self.date_to:
            domain.extend([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
        
        metrics = self.env['sports.performance.metric'].search(domain, order='date')
        
        # Group by month
        monthly_data = {}
        for metric in metrics:
            month_key = metric.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'total_metrics': 0,
                    'personal_bests': 0,
                    'avg_improvement': 0.0,
                    'improvements': []
                }
            
            monthly_data[month_key]['total_metrics'] += 1
            if metric.is_personal_best:
                monthly_data[month_key]['personal_bests'] += 1
            if metric.improvement:
                monthly_data[month_key]['improvements'].append(metric.improvement)
        
        # Calculate averages
        for month_data in monthly_data.values():
            if month_data['improvements']:
                month_data['avg_improvement'] = sum(month_data['improvements']) / len(month_data['improvements'])
        
        return monthly_data