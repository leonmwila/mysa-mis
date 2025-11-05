from odoo import models, fields, api

class SportsPerformanceMetric(models.Model):
    _name = 'sports.performance.metric'
    _description = 'Sports Performance Metrics'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Metric Name', required=True)
    athlete_id = fields.Many2one('sports.athlete', string='Athlete', required=True)
    
    # Event integration - using text field to avoid circular dependency
    # event_id = fields.Many2one('event.program', string='Event/Competition')
    event_name = fields.Char(string='Event/Competition Name')
    
    # Metric Details
    metric_type = fields.Selection([
        ('time', 'Time (seconds/minutes)'),
        ('distance', 'Distance (meters/km)'),
        ('score', 'Score/Points'),
        ('weight', 'Weight (kg)'),
        ('speed', 'Speed (km/h)'),
        ('height', 'Height (meters)'),
        ('percentage', 'Percentage (%)'),
        ('ranking', 'Ranking/Position'),
        ('other', 'Other')
    ], string='Metric Type', required=True)
    
    value = fields.Float(string='Value', required=True)
    unit = fields.Char(string='Unit of Measurement')
    
    # Context
    date = fields.Date(string='Date Recorded', required=True, default=fields.Date.today)
    location = fields.Char(string='Location')
    competition_level = fields.Selection([
        ('training', 'Training'),
        ('local', 'Local Competition'),
        ('regional', 'Regional Competition'),
        ('national', 'National Competition'),
        ('international', 'International Competition')
    ], string='Competition Level', default='training')
    
    # Performance Analysis
    is_personal_best = fields.Boolean(string='Personal Best')
    is_seasonal_best = fields.Boolean(string='Seasonal Best')
    previous_best = fields.Float(string='Previous Best')
    improvement = fields.Float(string='Improvement', compute='_compute_improvement')
    
    # Additional Information
    weather_conditions = fields.Char(string='Weather Conditions')
    equipment_used = fields.Char(string='Equipment Used')
    coach_notes = fields.Text(string='Coach Notes')
    notes = fields.Text(string='Additional Notes')
    
    # Status
    verified = fields.Boolean(string='Verified', default=False)
    verified_by_id = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime(string='Verification Date')

    @api.depends('value', 'previous_best')
    def _compute_improvement(self):
        for record in self:
            if record.previous_best and record.value:
                # For time-based metrics, improvement is negative (faster time)
                if record.metric_type == 'time':
                    record.improvement = record.previous_best - record.value
                else:
                    record.improvement = record.value - record.previous_best
            else:
                record.improvement = 0.0

    @api.model
    def create(self, vals_list):
        # Handle both single dict and list of dicts
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        result = super().create(vals_list)
        # Check if this is a personal best
        result._check_personal_best()
        return result

    def write(self, vals):
        result = super().write(vals)
        if 'value' in vals:
            self._check_personal_best()
        return result

    def _check_personal_best(self):
        """Check if this metric is a personal best for the participant"""
        for record in self:
            # Get all metrics of the same type for this athlete
            similar_metrics = self.search([
                ('athlete_id', '=', record.athlete_id.id),
                ('metric_type', '=', record.metric_type),
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ])
            
            if similar_metrics:
                # For time-based metrics, lower is better
                if record.metric_type == 'time':
                    best_value = min(similar_metrics.mapped('value'))
                    record.is_personal_best = record.value < best_value
                else:
                    # For other metrics, higher is usually better
                    best_value = max(similar_metrics.mapped('value'))
                    record.is_personal_best = record.value > best_value
                
                record.previous_best = best_value
            else:
                # First record is automatically a personal best
                record.is_personal_best = True

    def action_verify(self):
        """Verify the performance metric"""
        self.verified = True
        self.verified_by_id = self.env.user.id
        self.verification_date = fields.Datetime.now()

    def action_view_athlete_metrics(self):
        """View all performance metrics for this athlete"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.athlete_id.name} - Performance Metrics',
            'res_model': 'sports.performance.metric',
            'view_mode': 'list,form,graph',
            'domain': [('athlete_id', '=', self.athlete_id.id)],
            'context': {'default_athlete_id': self.athlete_id.id}
        }