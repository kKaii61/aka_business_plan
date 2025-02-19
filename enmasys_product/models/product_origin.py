# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ProductOrigin(models.Model):
    _name = 'product.origin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Nguồn sản phẩm'

    name = fields.Char('Tên nguồn', required=True, tracking=True)
    code = fields.Char('Mã nguồn', required=True, size=1, index=True, tracking=True)

    _sql_constraints = [('code_unique', 'unique(code)', 'Mã đã tồn tại trong hệ thống!')]

