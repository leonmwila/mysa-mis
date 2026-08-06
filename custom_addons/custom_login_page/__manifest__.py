{
    'name': 'Custom Login Page',
    'version': '1.0.2',
    'summary': 'Customize Odoo login page elements',
    'category': 'Tools',
    'author': 'Smart Zambia Institute',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [
        'views/web_login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_login_page/static/src/scss/login_background.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}