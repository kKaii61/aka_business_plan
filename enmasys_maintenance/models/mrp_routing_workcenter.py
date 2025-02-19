from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MrpBom(models.Model):
    _inherit = 'mrp.routing.workcenter'

    block_id = fields.Many2one('maintenance.equipment', 'Maintenance Mold')
    machine_id = fields.Many2one('maintenance.equipment', 'Maintenance Machine')
    cycle = fields.Float('Cycle')
    time_cycle_manual = fields.Float(
        'Manual Duration', default=60,
        help="Time in minutes:"
             "- In manual mode, time used"
             "- In automatic mode, supposed first time when there aren't any work orders yet",
        compute='compute_time_cycle_manual', store=True)

    @api.depends('cycle','bom_id.product_qty')
    def compute_time_cycle_manual(self):
        for record in self:
            record.time_cycle_manual = record.cycle * record.bom_id.product_qty

