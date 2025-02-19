# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

TYPE_CODE = {
    'product': '1',
    'service': '2',
    'consu': '3',
    'combo': '4',
    'event': '5',
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_origin_id = fields.Many2one('product.origin', 'Nguồn', required=True, index=True, tracking=True)
    x_brand_id = fields.Many2one('product.brand', 'Thương hiệu', required=True, index=True, tracking=True)
    x_type_id = fields.Many2one('product.type', 'Chủng loại', required=True, index=True, tracking=True)
    x_type_detail_id = fields.Many2one('product.type.detail', 'Chi tiết chủng loại', required=True,
                                       domain="[('product_type_id', '=', x_type_id)]", index=True, tracking=True)
    x_prefix = fields.Char('Prefix')
    x_next_sequence = fields.Integer('Next sequence', default=0)
    x_code_old = fields.Char('Mã cũ')

    @api.onchange('x_type_id')
    def _onchange_x_type_id(self):
        self.x_type_detail_id = None

    @api.model
    def create(self, vals):
        try:
            res = super(ProductTemplate, self).create(vals)
            prefix = f"{TYPE_CODE.get(res.type)}{res.x_origin_id.code}{res.x_brand_id.code}{res.x_type_id.code}{res.x_type_detail_id.code}"
            product_tmpl_id = self.env[self._name].search([('x_prefix', '=', prefix)], order='x_next_sequence desc', limit=1)

            number = product_tmpl_id.x_next_sequence or 1
            suffix = f'{number:05d}'
            default_code = f'{prefix}.{suffix}'
            res.write({
                'default_code': default_code,
                'x_prefix': prefix,
                'x_next_sequence': number + 1,
            })
            return res
        except Exception as e:
            raise ValidationError(e)
