# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductType(models.Model):
    _name = 'product.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Chủng loại sản phẩm'

    name = fields.Char('Tên loại', required=True, tracking=True)
    code = fields.Char('Mã loại', required=True, size=2, index=True, tracking=True)

    _sql_constraints = [('code_unique', 'unique(code)', 'Mã đã tồn tại trong hệ thống!')]

    line_ids = fields.One2many('product.type.detail', 'product_type_id', 'Chi tiết')


class ProductTypeDetail(models.Model):
    _name = 'product.type.detail'
    _description = 'Chi tiết chủng loại sản phẩm'

    name = fields.Char('Tên', required=True)
    code = fields.Char('Mã', required=True, size=2, index=True)
    product_type_id = fields.Many2one('product.type', 'Chủng loại sản phẩm', required=True, index=True)
