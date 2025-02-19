# -*- coding: utf-8 -*-
{
    'name': "Enmasys Cost Price",

    'summary': """
       Calculate cost of product """,

    'description': """
       Calculate cost of product
    """,

    'author': "Enmasys",
    'website': "https://enmasys.com/",

    'category': 'Manufacturing/Manufacturing',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'stock', 'mrp', 'account'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/res_allocation.xml',
        'views/mrp_bom.xml',
        'views/mrp_production.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
