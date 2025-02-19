# -*- coding: utf-8 -*-
{
    'name': "Enmasys Account",
    'summary': """Enmasys Account """,
    'description': """""",
    'author': 'Enmasys',
    'company': 'Enmasys',
    'maintainer': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': 'Reporting',
    'version': '17.0.1.0.1',
    'sequence': 110,
    'depends': ['base', 'account', 'base_account_budget'],
    'data': [
        'views/menu_item.xml',
        'views/account_move.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False
}
