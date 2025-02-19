import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHolidayDataReport(models.TransientModel):
    _name = "hr.holiday.data.report"
    _description = "Holiday Data Report"

    display_name = fields.Char(default="Báo cáo nghỉ phép", string="Display name")

    # inverse_name
    x_report_id = fields.Many2one(comodel_name="hr.holiday.report", string="Holiday Report", ondelete="cascade")

    # in4
    x_employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee",)
    x_employee_position_id = fields.Many2one(comodel_name="hr.job", related="x_employee_id.job_id", store=True)
    x_department_id = fields.Many2one(comodel_name="hr.department", related="x_employee_id.department_id", store=True)
    x_remaining_holiday_last_year = fields.Float(string="Remaining Leave from last year")
    x_used_of_remaining_holiday_last_year = fields.Float(string="Remaining Leave from last year (used)")
    x_allocated_intervals = fields.Float(string="Allocated Intervals")
    x_validated_holiday_requests = fields.Float(string="Validated Holiday-requests")
    x_used_leaves = fields.Float(string="Used leaves")
    x_remaining_leave = fields.Float(string="Remaining Leaves")