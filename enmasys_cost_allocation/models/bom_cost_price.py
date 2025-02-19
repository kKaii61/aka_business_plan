# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BomCostPrice(models.Model):
    _name = 'bom.cost.price'
    _description = 'Chi phí cho BOM'

    bom_id = fields.Many2one('mrp.bom', 'BOM', required=True)
    account_debt_id = fields.Many2one('account.account', 'Tài khoản nợ', required=True)
    account_credit_id = fields.Many2one('account.account', 'Tài khoản có', required=True)
    price_unit = fields.Float('Đơn giá', default=0)
    amount = fields.Float('Thành tiền', default=0)

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        try:
            self.amount = self.bom_id.product_qty * self.price_unit
        except Exception as e:
            raise ValidationError(e)

    @api.constrains('account_debt_id', 'account_credit_id')
    def _check_account(self):
        try:
            if self.account_debt_id == self.account_credit_id:
                raise UserError(_('Tài khoản nợ, có phải khác nhau!'))
        except Exception as e:
            raise ValidationError(e)
