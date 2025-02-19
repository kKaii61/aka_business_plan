from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for rec in self:
            for employee in rec.x_labor:
                employee.write({
                    'quant_product_mrp': rec.product_qty + employee.quant_product_mrp
                })
        return res
