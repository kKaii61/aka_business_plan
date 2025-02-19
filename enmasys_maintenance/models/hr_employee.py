from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # block_ids = fields.Many2many('maintenance.block', 'hr_employee_maintenance_block_rel', string='Block')
    # machine_ids = fields.Many2many('maintenance.machine', 'hr_employee_maintenance_machine_rel', string='Machine')
    quant_product_mrp = fields.Float('Quantity Products Produced')
    equipment_ids = fields.Many2many('maintenance.equipment', 'hr_employee_maintenance_equipment_rel', string='Equipment')
