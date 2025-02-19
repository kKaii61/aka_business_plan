# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    parent_account = fields.Many2one('account.account', string='Tài khoản mẹ')
