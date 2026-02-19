{
    'name': 'Venues Management',
    'version': '1.0.0',
    'author': 'Smart Zambia Institute',
    'category': 'Operations',
    'summary': 'Shared venue registry for arts, sports, and youth programs',
    'description': '''
        Shared Venues Management

        Features:
        - Centralized venue registry
        - Reusable across Artist, Sports, and Youth modules
        - Venue capacity and contact management
        - Facilities and availability details
    ''',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/venue_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
