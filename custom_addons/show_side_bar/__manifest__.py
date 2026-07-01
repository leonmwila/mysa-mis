{
    'name': 'Show Side Bar',
    'version': '1.1.0',
    'summary': 'Keep the Odoo app sidebar visible by default in backend',
    'category': 'Tools',
    'author': 'Smart Zambia Institute',
    'license': 'LGPL-3',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'show_side_bar/static/src/js/show_side_bar.js',
            'show_side_bar/static/src/scss/show_side_bar.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
