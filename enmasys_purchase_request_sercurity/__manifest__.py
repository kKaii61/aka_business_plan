# -*- coding: utf-8 -*-
{
    'name': "Enmasys Purchase Request Sercurity",
    'summary': """Enmasys Purchase Request Sercurity """,
    'description': """""",
    'author': 'Enmasys',
    'company': 'Enmasys',
    'maintainer': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': 'Purchase Request Surcurity',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'purchase','purchase_request'],
    'data': [
        # 'data/aggregate_cost_detail_data.xml',
        'security/sercurity.xml',
        'security/ir.model.access.csv',

        # 'wizard/aggregate_cost_views.xml',
        # 'views/product_cost.xml',
        'views/purchase_request_view.xml',
        'views/menus.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False
}
