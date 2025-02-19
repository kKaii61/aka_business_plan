# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResAllocation(models.Model):
    _name = 'res.allocation'
    _description = 'Phân bổ chi phí'

    account_ids = fields.Many2many('account.account', 'allocation_account_rel', 'allocation_id', 'account_id', 'Tài khoản chi phí',
                                   required=True, index=True)
    account_dest_ids = fields.Many2many('account.account', 'allocation_account_dest_rel', 'allocation_id', 'account_id',
                                        'Tài khoản chi phí')
    account_mrp_id = fields.Many2one('account.account', 'Tài khoản chi phí sản xuất dở dang', required=True)
    type = fields.Selection([
        ('material', 'Theo nguyên vật liệu chính'),
        ('other_account', 'Theo tỷ lệ phân bổ của tài khoản khác'),
        ('bom_price', 'Theo đơn giá định mức'),
    ], 'Loại phân bổ', required=True)

    company_id = fields.Many2one('res.company', 'Công ty', default=lambda self: self.env.company, required=True)

    @api.onchange('type')
    def _onchange_type(self):
        try:
            if self.type != 'other_account':
                self.account_dest_ids = None
        except Exception as e:
            raise ValidationError(e)

    @api.constrains('account_ids', 'account_dest_ids')
    def _check_accounts(self):
        try:
            if any(account in self.account_dest_ids for account in self.account_ids) or any(
                    account in self.account_ids for account in self.account_dest_ids):
                raise ValidationError(_('Tài khoản bị trùng trên cùng bản ghi!'))
            allocation_ids = self.env['res.allocation'].sudo().search([('id', '!=', self.id), ('company_id', '=', self.company_id.id)])
            for allocation in allocation_ids:
                if any(account in allocation.account_ids for account in self.account_ids):
                    raise ValidationError(_('Có tài khoản đã được cấu hình'))
        except Exception as e:
            raise ValidationError(e)

    @api.depends('account_ids', 'type', 'account_dest_ids')
    def _compute_display_name(self):
        try:
            for rc in self:
                account_name = '-'.join([account.code for account in rc.account_ids]) if rc.account_ids else ''
                name = account_name + ' - ' + dict(self._fields['type'].selection).get(rc.type)
                if rc.type == 'other_account':
                    account_dest_name = '-'.join([account.code for account in rc.account_dest_ids]) if rc.account_dest_ids else ''
                    name = name + ' - ' + account_dest_name

                rc.display_name = name
        except Exception as e:
            raise ValidationError(e)
