from odoo import api, fields, models, tools, SUPERUSER_ID, _
from lxml import etree
from odoo.exceptions import AccessError, ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for picking in self.picking_ids:
            picking.write({
                'commitment_date': self.commitment_date
            })
        return res
