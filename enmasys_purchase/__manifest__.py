# -*- coding: utf-8 -*-
{
    'name': "Enmasys Purchase Order",
    'summary': """Enmasys Purchase Order """,
    'description': """""",
    'author': 'Enmasys',
    'company': 'Enmasys',
    'maintainer': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': 'Reporting',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'purchase'],
    'data': [
        # 'data/aggregate_cost_detail_data.xml',
        # 'security/ir.model.access.csv',
        # 'wizard/aggregate_cost_views.xml',
        # 'views/product_cost.xml',
        'views/purchase_order_view.xml',
        # 'views/production_inventory.xml',
    ],
'assets': {
        'web.assets_backend': [
            'enmasys_purchase/static/src/css/width_column_fields.scss',

        ],

    },
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False
}
