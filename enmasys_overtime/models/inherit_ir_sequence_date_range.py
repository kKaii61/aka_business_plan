import logging

from odoo import models, fields


_logger = logging.getLogger(__name__)


class InheritIrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"
    _name = "ir.sequence.date_range"

    x_leave_type_id = fields.Many2one(comodel_name="hr.leave.type", string="Leave type")
