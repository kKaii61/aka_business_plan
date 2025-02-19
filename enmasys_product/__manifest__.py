# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Enmasys Product',
    'summary': 'Enmasys Product',
    'description': """Odoo 17 Enmasys Product""",
    'author': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': '',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'product'],
    'demo': [],

    'data': [
        'security/ir.model.access.csv',
        'views/product_origin.xml',
        'views/product_brand.xml',
        'views/product_type.xml',
        'views/product_template.xml',
    ],
    'assets': {
    },
    'installable': True,
    'application': False,
}
