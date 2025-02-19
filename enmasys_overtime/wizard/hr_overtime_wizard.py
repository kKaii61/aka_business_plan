import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrOvertimeWizard(models.TransientModel):
    _name = "hr.overtime.wizard"
    _description = "Overtime Wizard"

    x_message = fields.Char(string="Message")

    x_overtime_ids = fields.Many2many(
        comodel_name="hr.overtime", string="Overtimes",
        relation="hr_overtime_hr_overtime_wizard_rel", column1="overtime_id", column2="wizard_id")

    def approve_overtimes_after_reconfirm(self):
        return self.x_overtime_ids.action_approve()
