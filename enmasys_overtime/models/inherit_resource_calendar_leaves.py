from odoo import models, fields


class InheritResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    x_overtime_id = fields.Many2one(comodel_name="hr.overtime", string="Overtime", tracking=True)
    time_type = fields.Selection(selection_add=[('overtime', "Overtime")], ondelete={'overtime': "set default"})