{
    'name': 'Associations & Organizations',
    'version': '1.0.0',
    'author': 'Smart Zambia Institute',
    'category': 'Operations',
    'summary': 'Central registry for associations and organizations across Sports, Arts, and Youth',
    'description': '''
        Associations & Organizations

        Centralized management for entities that can be used by:
        - Sports Tracking & Analytics
        - Artist Tracking
        - Youth Tracking

        A single entity can be linked to one, two, or all three domains.
    ''',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/common_association_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
