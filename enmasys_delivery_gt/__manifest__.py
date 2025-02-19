# -*- coding: utf-8 -*-
{
    'name': "Enmasys Delivery GT",

    'summary': """
        Enmasys Delivery GT """,

    'description': """
        Enmasys Delivery GT
    """,

    'author': "Enmasys",
    'website': "https://enmasys.com/",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'stock',  'sale', 'sale_stock'
    ],

    # always loaded
    'data': [

        'data/sequence_delivery.xml',
        'security/ir.model.access.csv',

        'views/tradition_delivery_view.xml',
        'views/stock_picking_view.xml',
        'views/menus.xml',


    ],
    'application': True,
}
