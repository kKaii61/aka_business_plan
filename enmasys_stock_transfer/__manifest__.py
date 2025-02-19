# -*- coding: utf-8 -*-
{
    'name': "Stock Transfer",
    'summary': """
        Internal transfers between warehouses
    """,

    'description': """
        Internal transfers between warehouses
    """,
    'author': "CND",
    'category': 'Stock',
    'version': '0.1',
    'depends': ['base', 'stock', ],
    'data': [
        'views/stock_warehouse.xml',
        'views/stock_picking.xml',
        'views/inherit_stock_picking_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
