from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.equipment'

    #Block
    product_ids = fields.Many2many('product.product','maintenance_equipment_product_product_rel',string='Product')
    weight = fields.Float('Weight')
    time_used = fields.Float('Time Used')
    state_block = fields.Selection(
        selection=[
            ('using', 'Using'),
            ('idle', 'Idle'),
            ('maintenance', 'Maintenance'),
        ],
        string='Status',
        tracking=True,
        default='using',
    )
    #Machine
    type = fields.Selection(
        selection=[
            ('genuine_machine', 'Genuine Machine'),
            ('old_machine', 'Old Machine'),
        ],
        string='Type',
        tracking=True,
        default='genuine_machine',
    )
    state_machine = fields.Selection(
        selection=[
            ('using', 'Using'),
            ('idle', 'Idle'),
            ('maintenance', 'Maintenance'),
        ],
        string='Status',
        tracking=True,
        default='using',
    )
    cycle = fields.Float('Cycle')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Centers')

