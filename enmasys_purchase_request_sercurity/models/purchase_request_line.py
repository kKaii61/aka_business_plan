from odoo import api, fields, models, tools, SUPERUSER_ID


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    partner_id = fields.Many2one('res.partner',string="Nhà cung cấp")
