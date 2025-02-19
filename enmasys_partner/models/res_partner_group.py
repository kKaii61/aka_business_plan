# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerGroup(models.Model):
    _name = 'res.partner.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Nhóm liên hệ'

    name = fields.Char('Tên nhóm', required=True, tracking=True)
    code = fields.Char('Mã nhóm', required=True, index=True, tracking=True)
    sequence_id = fields.Many2one('ir.sequence', 'Trình tự', tracking=True)

    _sql_constraints = [('code_unique', 'unique(code)', 'Mã đã tồn tại trong hệ thống!')]

    @api.model
    def create(self, vals):
        try:
            if not vals.get('sequence_id'):
                vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                    'name': vals.get('name') + ' ' + _('Trình tự') + ' ' + vals.get('code'),
                    'code': self._name,
                    'prefix': vals.get('code') + '.',
                    'padding': 6,
                    'company_id': False,
                    'number_next': 1,
                    'number_increment': 1
                }).id

            return super(ResPartnerGroup, self).create(vals)
        except Exception as e:
            raise ValidationError(e)
