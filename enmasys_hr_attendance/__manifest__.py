# -*- coding: utf-8 -*-
{
    'name': "Enmasys HR Attendance",

    'summary': """
        Enmasys HR Attendance """,

    'description': """
        Enmasys HR Attendance
    """,

    'author': "Enmasys",
    'website': "https://enmasys.com/",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'hr_attendance'
    ],

    # always loaded
    'data': [
        'views/inherit_hr_attendance_views.xml',
    ],
    'application': True,
}
