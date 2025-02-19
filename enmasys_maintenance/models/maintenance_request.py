from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    block_id = fields.Many2one('maintenance.block', 'Maintenance Block')
    machine_id = fields.Many2one('maintenance.machine', 'Maintenance Machine')
