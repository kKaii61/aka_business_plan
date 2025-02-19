from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MaintenanceMachine(models.Model):
    _name = "maintenance.machine"
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
    type = fields.Selection(
        selection=[
            ('genuine_machine', 'Genuine Machine'),
            ('old_machine', 'Old Machine'),
        ],
        string='Type',
        tracking=True,
        default='genuine_machine',
    )
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
    cycle = fields.Float('Cycle')
    workcenter_id = fields.Many2one('mrp.workcenter','Work Centers')

    maintenance_ids = fields.One2many('maintenance.request', 'machine_id')