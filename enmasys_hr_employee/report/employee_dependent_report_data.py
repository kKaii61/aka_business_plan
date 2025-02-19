import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class EmployeeDependentReportData(models.TransientModel):
    _name = "employee.dependent.report.data"
    _description = "Report-data: Employee Dependents"
    _order = "x_employee_id"

    # inverse_name
    x_report_id = fields.Many2one(
        comodel_name="employee.dependent.report", string="Report: Employee Dependents", ondelete="cascade")

    # in4
    x_dependence_line_id = fields.Many2one(
        comodel_name="hr.employee.dependence.contact.line", string="Root Dependence data")
    x_employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Nhân viên", related="x_dependence_line_id.x_hr_employee_id")
    x_employee_ref = fields.Char(string="Employee block",)
    x_employee_name = fields.Char(string="Employee block", related="x_employee_id.name")
    x_employee_block = fields.Char(string="Employee block",)
    x_employee_gender = fields.Selection(string="Giới tính", related="x_employee_id.gender", store=True)
    x_employee_department_id = fields.Many2one(
        comodel_name="hr.department", string="Phòng ban", related="x_employee_id.department_id")

    x_dependent_name = fields.Char(string="Họ tên người thân", related="x_dependence_line_id.x_dependent_contact_name")
    x_dependent_dob = fields.Date(
        string="Ngày sinh", related="x_dependence_line_id.x_dependent_contact_birthdate")
    x_dependent_relationship_type_id = fields.Many2one(
        comodel_name="relatives.type", string="Mối quan hệ",
        related="x_dependence_line_id.x_dependent_contact_relationship_id")
