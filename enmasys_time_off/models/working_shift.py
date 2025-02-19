from odoo import models, fields, _


class WorkingShift(models.Model):
    _name = "working.shift"
    _description = "Working shift"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "x_shift_name"

    # new
    x_shift_name = fields.Char(string="Shift name", required=True, tracking=True)
    x_shift_from = fields.Float(string="Shift from", required=True, tracking=True)
    x_shift_to = fields.Float(string="Shift to", required=True, tracking=True)
