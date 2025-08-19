{
    'name': 'Hospital - Insurance Management',
    'version': '1.0',
    'summary': 'Manage insurance companies and auto-pay patient invoices',
    'depends': ['hms_base','base', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/insurance_claim_sequence.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/account_move_views.xml',
        'views/insurance_company_views.xml',
        'views/res_partner_views.xml',
        'views/insurance_claim_views.xml',
    ],
    'installable': True,
    'application': False,
}
