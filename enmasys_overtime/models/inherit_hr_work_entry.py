from odoo import models, fields


class InheritHrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    x_overtime_id = fields.Many2one(comodel_name="hr.overtime", string="Overtime", tracking=True)