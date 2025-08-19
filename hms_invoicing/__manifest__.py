{
    'name': 'Hospital - Invoicing Management',
    'version': '1.0',
    'summary': 'Create patient invoices and add lines',
    'depends': ['hms_base','account', 'hms_patient'],
    'data': [
        'views/actions.xml',
        'views/menus.xml'
    ],
    'installable': True,
    'application': False,
}
