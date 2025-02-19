# -*- coding: utf-8 -*-
{
    'name': "Enmasys Purchase Order Request",
    'summary': """Enmasys Purchase Order Request""",
    'description': """""",
    'author': 'Enmasys',
    'company': 'Enmasys',
    'maintainer': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': 'Reporting',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'enmasys_purchase', 'purchase_request'],
    'data': [
        # 'data/aggregate_cost_detail_data.xml',
        'security/security.xml',
        # 'wizard/aggregate_cost_views.xml',
        # 'views/product_cost.xml',
        'views/purchase_order_view.xml',
        # 'views/production_inventory.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False
}
