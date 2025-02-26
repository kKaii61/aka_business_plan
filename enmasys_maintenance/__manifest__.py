# -*- coding: utf-8 -*-
{
    'name': "Enmasys Maintenance",
    'summary': """Enmasys Maintenance""",
    'description': """""",
    'author': 'Enmasys',
    'company': 'Enmasys',
    'maintainer': 'Enmasys',
    'website': 'https://enmasys.com/',
    'category': 'Reporting',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 110,
    'depends': ['base', 'maintenance','mrp','hr','enmasys_cost_allocation'],
    'data': [
        # 'data/aggregate_cost_detail_data.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        # 'wizard/aggregate_cost_views.xml',
        'views/hr_employee_view.xml',
        'views/maintenance_equipment_view.xml',
        'views/mrp_routing_workcenter_view.xml',
        'views/maintenance_machine_view.xml',
        'views/maintenance_block_view.xml',
        'views/maintenance_request_view.xml',
        # 'views/menus.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False
}
