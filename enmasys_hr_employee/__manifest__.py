{
    'name': "Enmasys Hr Employee",
    'version': '1.0',
    'depends': [
        'base', 'base_setup', 'hr', 'hr_contract'
    ],
    'author': "Enmasys",
    'description': """
            Enmasys Hr Employee
    """,
    # data files always loaded at installation
    'data': [
        # DATA

        # SECURITY
        'security/ir.model.access.csv',

        # WIZARD

        # VIEWS
        'views/hr_employee_view.xml',
        'views/relatives_type.xml',

        # report
        'report/report_number_of_worker_views.xml',
        'report/employee_dependent_report_view.xml',
        'report/employee_information_report.xml',
        'report/hr_contract_employee_report.xml',
        'report/report_salary_according_to_contract.xml',
        # 'views/inherit_hr_attendance_menus.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
}
