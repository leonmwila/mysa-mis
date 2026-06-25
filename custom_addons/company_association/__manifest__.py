{
    'name': 'Company as Association / Organization',
    'version': '1.0.0',
    'author': 'Smart Zambia Institute',
    'category': 'Operations',
    'summary': 'Allows Companies to act as Associations and Organizations in the MYSA MIS',
    'description': '''
        Company as Association / Organization

        Extends res.company with all the fields from the Associations & Organizations
        module, allowing companies (e.g. Youth Associations, Sports Associations) to:
        - Be typed as Association, Organization, or Institution
        - Have usage domain flags (Sports, Arts, Youth)
        - Carry an Organization Status
        - Appear in the Associations & Organizations registry

        This enables external associations and organizations to log in as a company
        and manage their own data entries (Youth, Athletes, Teams, etc.).
    ''',
    'depends': ['base', 'mail', 'associations_organizations'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/company_association_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
