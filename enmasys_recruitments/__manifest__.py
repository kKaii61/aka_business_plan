# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Enmasys: Recruitments",
    'version': '17.0.0.8386',
    'category': 'Human Resources/Recruitment',
    'sequence': 8386,
    'summary': "Enmasys: Recruitments",
    'website': "https://enmasys.com/",
    'depends': [
        'hr_recruitment_skills'
    ],
    'data': [
        # data
        'data/recruitment_sequences.xml',

        # security
        'security/ir.model.access.csv',

        # report

        # wizard

        # views
        'views/recruitment_request_position_views.xml',
        'views/recruitment_request_views.xml',
        'views/inherit_hr_applicant_views.xml',
    ],
    'demo': [

    ],
    'assets': {
        'web.assets_backend': [],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
