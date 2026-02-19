{
    'name': 'Teams and Groups Management',
    'version': '1.0.0',
    'author': 'Smart Zambia Institute',
    'category': 'Arts & Sports Management',
    'summary': 'Manage sports teams and artist bands/groups with achievement tracking',
    'description': '''
        Teams and Groups Management System
        
        Features:
        - Sports Team management for athletes
        - Artist Band/Group management
        - Team and Band participation in events and programs
        - Team and Band achievement tracking
        - Automatic member achievement assignment when team/band wins
        - Solo or team/band participation options
    ''',
    'depends': [
        'base',
        'mail',
        'calendar',
        'sports_tracking',
        'artist_tracking',
        'associations_organizations',
        'event_program_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/teams_groups_security.xml',
        'data/teams_groups_data.xml',
        'views/sports_team_views.xml',
        'views/artist_band_views.xml',
        'views/team_achievement_views.xml',
        'views/band_achievement_views.xml',
        'views/achievement_extension_views.xml',
        'views/association_extension_views.xml',
        'views/event_extension_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

