{
    'name': 'Artist Tracking & Analytics',
    'version': '1.0',
    'author': 'Smart Zambia Institute',
    'category': 'Arts Management',
    'summary': 'Track artists, performance metrics, and generate arts analytics',
    'description': '''
        Artist Tracking & Analytics System
        
        Features:
        - Artist registry and management (Dancers, Musicians, Painters, Actors, etc.)
        - Performance metrics and portfolio tracking
        - Arts associations management
        - Artist achievements and awards tracking
        - Analytics dashboards and reports
        - Zone-based arts management
        - Integration with event management
        - Artist validation through associations
    ''',
    'maintainer': 'Smart Zambia Institute',
    'website': 'mays.gov.zm',
    'license': 'AGPL-3',
        'depends': [
        'base',
        'mail',
        'calendar',
        'event_program_management',  # For event integration
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data files
        'data/artist_data.xml',
        
        # Views
        'views/actions.xml',
        'views/artist_views.xml',
        'views/association_views.xml',
        'views/performance_views.xml',
        'views/achievement_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 40,
}