# -*- coding: utf-8 -*-
{
    'name': 'Quickbooks Integration',
    'author': 'UP5TECH',
    'version': '14.0.0.0',
    'live_test_url': ' ',
    'summary': 'Quickbooks Integration',
    'description': """Quickbooks Integration""",
    'license': "OPL-1",
    'depends': ['account', 'sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/qbi_settings.xml',
    ],
    'installable': True,
    'auto_install': False,
    'category': 'Customizations',

    'external_dependencies': {
        'python': ['urllib3', 'dateutil', 'intuit-oauth', 'python-quickbooks']
    }
}
