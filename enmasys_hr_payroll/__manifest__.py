# -*- coding: utf-8 -*-
{
    'name': "Enmasys HR Payroll",

    'summary': """
        Enmasys HR Payroll """,

    'description': """
        Enmasys HR Payroll
    """,

    'author': "Enmasys",
    'website': "https://enmasys.com/",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'hr_payroll'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # report
        'report/report_payslip_views.xml',
        'report/social_insurance_report_views.xml',
    ],
    'application': True,
}
