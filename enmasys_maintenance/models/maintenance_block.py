from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MaintenanceBlock(models.Model):
    _name = "maintenance.block"
    _description = "Maintenance Block"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'maintenance.mixin']

    # like equipment
    owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    name = fields.Char('Equipment Name', required=True, translate=True)
    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee')
    employee_id = fields.Many2one('hr.employee', string='Assigned Employee', tracking=True)
    assign_date = fields.Date('Assigned Date', tracking=True)
    scrap_date = fields.Date('Scrap Date')
    location = fields.Char('Location')
    note = fields.Html('Note')
    partner_id = fields.Many2one('res.partner', string='Vendor', check_company=True)
    partner_ref = fields.Char('Vendor Reference')
    model = fields.Char('Model')
    serial_no = fields.Char('Serial Number', copy=False)
    cost = fields.Float('Cost')
    warranty_date = fields.Date('Warranty Expiration Date')
    category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category',
                                  tracking=True)

    # diff block
    code = fields.Char('Code')
    product_ids = fields.Many2many('product.product','maintenance_block_product_product_rel','Product')
    weight = fields.Float('Weight')
    time_used = fields.Float('Time Used')
    state = fields.Selection(
        selection=[
            ('using', 'Using'),
            ('idle', 'Idle'),
            ('maintenance', 'Maintenance'),
        ],
        string='Status',
        tracking=True,
        default='using',
    )
    maintenance_ids = fields.One2many('maintenance.request', 'block_id')
