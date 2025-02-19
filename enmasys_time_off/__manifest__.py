{
    'name': "Enmasys: Time Off",
    'version': '1.0',
    'depends': [
        'base', 'base_setup', 'hr_holidays', 'hr_attendance', 'hr',
    ],
    'author': "Enmasys",
    'description': """
            Enmasys: Time off
    """,
    # data files always loaded at installation
    'data': [
        # DATA

        # SECURITY
        # 'security/inherit_hr_attendance_rules.xml',
        'security/ir.model.access.csv',

        # WIZARD

        # VIEWS
        'views/inherit_hr_employee_views.xml',
        'views/working_shift_views.xml',
        'views/working_shift_register_views.xml',
        # 'views/working_shift_register_template.xml',

        'views/inherit_time_off_menus.xml',
        'views/inherit_hr_attendance_menus.xml',
    ],
    'demo': [

    ],
    # 'assets': {
    #         'web.assets_backend': [
    #             # 'to_org_chart/static/src/scss/org_chart_view.scss',
    #             'enmasys_time_off/static/src/js/working_shift_register_controller_mixin.js',
    #             'enmasys_time_off/static/src/js/working_shift_register_gantt.js'
    #             ],
    #         # 'web.qunit_suite_tests': [
    #         #     'to_org_chart/static/tests/**/*'
    #         #     ]
    #         },
    'installable': True,
    'application': True,
}
