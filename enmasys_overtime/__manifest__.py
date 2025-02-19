# -*- coding: utf-8 -*-

{
    'name': "Enmasys: Overtime",
    'summary': "Enmasys: Overtime",
    'description': "Enmasys: Overtime",
    'author': "Enmasys",
    'website': "https://enmasys.com/",
    'category': 'Human Resources/Holidays',
    'version': '17.0.0.1',
    'license': 'LGPL-3',
    'depends': [
        'base', 'hr_work_entry_holidays', 'uom',
    ],
    # always loaded
    'data': [
        # data
        'data/overtime_sequences.xml',
        'data/working_uom.xml',

        # security
        'security/ir.model.access.csv',

        # report

        # wizard
        'wizard/inherit_res_config_settings_views.xml',
        'wizard/hr_overtime_wizard_views.xml',
        'wizard/over_time_report_views.xml',
        'wizard/hr_holiday_report_views.xml',

        # view
        'views/inherit_ir_sequence_views.xml',
        'views/hr_overtime_views.xml',
        'views/inherit_hr_leave_type_views.xml',
    ],
    'application': True,
    'installable': True,
}
