{
    'name': 'Hospital - Discount Request Management',
    'version': '1.0',
    'summary': 'Manage patient discount requests for invoices',
    'depends': ['hms_base', 'hms_invoicing', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/discount_request_sequence.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/discount_request_views.xml',
    ],
    'installable': True,
    'application': False,
}