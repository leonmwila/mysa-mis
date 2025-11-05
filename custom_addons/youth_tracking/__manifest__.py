{
    'name': 'Youth Tracking & Empowerment',
    'version': '1.0.0',
    'author': 'Smart Zambia Institute',
    'category': 'Youth Management',
    'summary': 'Youth Program Management, Skills Training, CDF Applications & Empowerment Tracking',
    'description': '''
        Comprehensive Youth Management System for Ministry of Arts, Youth & Sports
        
        Features:
        - Youth Registration & Profile Management
        - CDF Application Processing & Tracking
        - Skills Training Program Management
        - Youth Empowerment Program Enrollment
        - Multi-level Approval Workflows
        - Program Participant Selection & Management
        - Youth Analytics & Reporting Dashboard
        - Zone-based Organization & Management
        - Achievement & Certification Tracking
        - Integration with Event Management System
    ''',
    'depends': [
        'base',
        'mail',
        'calendar',
        'event_program_management',
    ],
    'data': [
        'security/youth_security.xml',
        'security/ir.model.access.csv',
        'data/youth_data.xml',
        'views/youth_views.xml',
        'views/zone_views.xml',
        'views/application_views.xml',
        'views/other_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'youth_tracking/static/src/css/youth_dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}