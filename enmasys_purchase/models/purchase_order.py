from odoo import api, fields, models, tools, SUPERUSER_ID


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_import = fields.Boolean(string="Nhập khẩu")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.country_id:
                if rec.partner_id.country_id.code != 'VN':
                    rec.is_import = True
                else:
                    rec.is_import = False

    def print_quotation(self):
        return self.env.ref('purchase.report_purchase_quotation').report_action(self)