{
    'name': 'User Management',
    'version': 1.0,
    'author': 'Smart Zambia Institute',
    'category': 'Administration',
    'summary': 'Manages internal users, roles, councils, and departments',
    'description': 'This system Manages internal users, roles, councils, and departments',
    'depends': ['base'],
    'data': [
        'security/user_management_security.xml',
        'security/ir.model.access.csv',
        'views/user_profile_views.xml',
    ],
    'installable': True,
    'application': True
}