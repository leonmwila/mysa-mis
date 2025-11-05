{
    'name': 'Sports Tracking & Analytics',
    'version': '1.0',
    'author': 'Smart Zambia Institute',
    'category': 'Sports Management',
    'summary': 'Track athletes, performance metrics, and generate sports analytics',
    'description': '''
        Sports Tracking & Analytics System
        
        Features:
        - Athlete registry and management
        - Performance metrics tracking
        - Sports associations management
        - Winner and achievement tracking
        - Analytics dashboards and reports
        - Zone-based sports management
        - Integration with event management
    ''',
    'maintainer': 'Smart Zambia Institute',
    'website': 'mays.gov.zm',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'security/sports_tracking_security.xml',
        'data/sports_data.xml',
        'views/athlete_views.xml',
        'views/zone_association_views.xml',
        'views/performance_achievement_views.xml',
        'views/analytics_menu_views.xml',
        'views/analytics_graph_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 30,
}
