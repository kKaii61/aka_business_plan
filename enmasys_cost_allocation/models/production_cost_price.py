# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ProductionCostPrice(models.Model):
    _name = 'production.cost.price'
    _description = 'Chi phí cho lệnh sản xuất'

    production_id = fields.Many2one('mrp.production', 'Lệnh sản xuất', required=True)
    account_debt_id = fields.Many2one('account.account', 'Tài khoản nợ', required=True)
    account_credit_id = fields.Many2one('account.account', 'Tài khoản có', required=True)
    price_unit = fields.Float('Đơn giá', default=0, )
    amount = fields.Float('Thành tiền', default=0)
