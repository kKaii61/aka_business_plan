# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    x_level = fields.Selection([
        ('l1', 'L1'),
        ('l2', 'L2'),
        ('l3', 'L3'),
        ('l4', 'L4'),
        ('l5', 'L5')
    ], 'BOM Level', default='l1', required=True)

    x_is_allocation = fields.Boolean('Phân bổ chi phí chung', default=False)
    x_price_line_ids = fields.One2many('bom.cost.price', 'bom_id', 'Chi phí')

    @api.onchange('product_qty')
    def _onchange_set_amount(self):
        try:
            for line in self.x_price_line_ids:
                line.amount = self.product_qty * line.price_unit
        except Exception as e:
            raise ValidationError(e)

    @api.onchange('x_level', 'x_is_allocation')
    def _onchange_x_level(self):
        try:
            if self.x_level == 'l1' and not self.x_is_allocation:
                return {
                    'warning': {
                        'title': 'Warning!',
                        'message': 'Đây là thành phẩm cuối cùng, bạn có xác là không phân bổ chi phí chung cho định mức này?'}
                }
        except Exception as e:
            raise ValidationError(e)
