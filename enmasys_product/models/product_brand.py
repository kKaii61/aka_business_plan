# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ProductBrand(models.Model):
    _name = 'product.brand'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Thương hiệu sản phẩm'

    name = fields.Char('Tên thương hiệu', required=True, tracking=True)
    code = fields.Char('Mã thương hiệu', required=True, size=2, index=True, tracking=True)

    _sql_constraints = [('code_unique', 'unique(code)', 'Mã đã tồn tại trong hệ thống!')]
