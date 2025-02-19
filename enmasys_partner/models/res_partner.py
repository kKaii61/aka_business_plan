# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_code = fields.Char('Mã')
    x_group_id = fields.Many2one('res.partner.group', 'Nhóm liên hệ', tracking=True)

    @api.onchange('parent_id')
    def _onchange_parent_set_group(self):
        try:
            self.x_group_id = self.parent_id.x_group_id
        except Exception as e:
            raise ValidationError(e)

    # @api.model
    # def create(self, vals):
    #     try:
    #         if not vals.get('x_group_id') and not self.env.context.get('group_id'):
    #             raise UserError(_('Nhóm liên hệ là bắt buộc nhập'))
    #
    #         gid = vals.get('x_group_id') or self.env.context.get('group_id')
    #         group_id = self.env['res.partner.group'].sudo().browse(gid)
    #         vals['x_code'] = group_id.sequence_id.next_by_id()
    #         vals['x_group_id'] = gid
    #         return super(ResPartner, self).create(vals)
    #     except Exception as e:
    #         raise ValidationError(e)

    @api.depends('name', 'x_code')
    def _compute_display_name(self):
        try:
            for rc in self:
                if rc.x_code:
                    rc.display_name = f'[{rc.x_code}] {rc.name}'
                else:
                    rc.display_name = rc.name
        except Exception as e:
            raise ValidationError(e)

    def write(self, vals):
        try:
            if 'x_group_id' not in vals:
                return super(ResPartner, self).write(vals)

            if not vals.get('x_group_id') and not self.env.context.get('group_id'):
                raise UserError(_('Nhóm liên hệ là bắt buộc nhập'))

            gid = vals.get('x_group_id') or self.env.context.get('group_id')
            group_id = self.env['res.partner.group'].sudo().browse(gid)
            vals['x_code'] = group_id.sequence_id.next_by_id()
            return super(ResPartner, self).write(vals)
        except Exception as e:
            raise ValidationError(e)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        try:
            domain = domain or []
            if name:
                domain += [('x_code', operator, name)]
            return self._search(domain, limit=limit, order=order)
        except Exception as e:
            raise ValidationError(e)


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        try:
            group_id = self.env['res.partner.group'].sudo().search([('code', '=', 'NV')], limit=1)
            if not group_id:
                group_id = self.env['res.partner.group'].sudo().create({
                    'code': 'NV',
                    'name': 'Nhân viên'
                })
            return super(ResUser, self.with_context({'group_id': group_id.id})).create(vals)
        except Exception as e:
            raise ValidationError(e)
