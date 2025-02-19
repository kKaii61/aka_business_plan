# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model_create_multi
    def create(self, vals_list):
        try:
            # create missing partners
            no_partner_vals_list = [
                vals
                for vals in vals_list
                if vals.get('name') and not vals.get('partner_id')
            ]
            group_id = self.env['res.partner.group'].sudo().search([('code', '=', 'KH')], limit=1)
            if not group_id:
                group_id = self.env['res.partner.group'].sudo().create({
                    'code': 'KH',
                    'name': 'Khách hàng'
                })
            ctx = {
                'default_parent_id': False,
                'group_id': group_id.id,
            }
            if no_partner_vals_list:
                partners = self.env['res.partner'].with_context(ctx).create([
                    {
                        'name': vals['name'],
                        'is_company': True,
                        'image_1920': vals.get('logo'),
                        'email': vals.get('email'),
                        'phone': vals.get('phone'),
                        'website': vals.get('website'),
                        'vat': vals.get('vat'),
                        'country_id': vals.get('country_id'),
                    }
                    for vals in no_partner_vals_list
                ])
                # compute stored fields, for example address dependent fields
                partners.flush_model()
                for vals, partner in zip(no_partner_vals_list, partners):
                    vals['partner_id'] = partner.id

            return super(ResCompany, self).create(vals_list)
        except Exception as e:
            raise ValidationError(e)
