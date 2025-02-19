# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Enmasys Partner',
    'summary': 'Enmasys Partner',
    'description': """Odoo 17 Enmasys Partner""",
    'author': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': '',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'contacts', 'hr'],
    'demo': [],

    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_partner_group.xml',
        'views/res_partner.xml',
        'views/inherit_hr_employee_views.xml',
    ],
    'assets': {
    },
    'installable': True,
    'application': False,
}
