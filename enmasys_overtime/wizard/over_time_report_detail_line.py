import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class OverTimeReportDetailLine(models.TransientModel):
    _name = "over.time.report.detail.line"
    _description = "REPORT: OVER-TIME/detail"
    _order = "x_over_time_request_date desc, x_over_time_duration desc"

    x_employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    x_employee_position_id = fields.Many2one(
        comodel_name="hr.job", string="Employee's position", related="x_employee_id.job_id")
    x_employee_department_id = fields.Many2one(
        comodel_name="hr.department", string="Employee's department", related="x_employee_id.department_id")
    x_over_time_request_date = fields.Date(string="OVER-TIME request date")
    x_work_entry_type_id = fields.Many2one(comodel_name="hr.work.entry.type", string="Work-Entry-Type")
    x_over_time_duration = fields.Float(string="Duration (hour)")
    x_over_time_line_id = fields.Many2one(comodel_name="hr.overtime.interval", string="Origin OT-line")
    x_overtime_id = fields.Many2one(
        comodel_name="hr.overtime", string="Origin OT", related="x_over_time_line_id.x_overtime_id")
    x_over_time_state = fields.Selection(string="OVER-TIME's state", related="x_overtime_id.state", store=True)

