from odoo import _, api, fields, models


class InheritHrEmployee(models.Model):
    _inherit = 'hr.employee'

    # TAB: Dependent Contacts
    x_hr_employee_dependence_contact_line_ids = fields.One2many(
        comodel_name="hr.employee.dependence.contact.line", inverse_name="x_hr_employee_id",
        ondelete="cascade", string="Người phụ thuộc")

    x_social_insurance_no = fields.Char(string="Social Insurance No.", tracking=True, )
