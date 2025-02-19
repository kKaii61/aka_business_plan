from odoo import models, fields

from ..models.inherit_res_company import OVERTIME_INTERVALS


class InheritResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _name = "res.config.settings"

    x_over_time_lunch_from = fields.Float(
        string="Lunch from (HH:MM)", readonly=False, related="company_id.x_over_time_lunch_from")
    x_over_time_lunch_to = fields.Float(
        string="Lunch to (HH:MM)", readonly=False, related="company_id.x_over_time_lunch_to")

    x_default_estimated_ot_start_time = fields.Selection(
        selection=OVERTIME_INTERVALS,  readonly=False, related="company_id.x_default_estimated_ot_start_time",
        string="Default OT estimated start",)
    x_default_estimated_ot_end_time = fields.Selection(
        selection=OVERTIME_INTERVALS,  readonly=False, related="company_id.x_default_estimated_ot_end_time",
        string="Default OT estimated end",)
