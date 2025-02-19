# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    x_level = fields.Selection([
        ('l1', 'L1'),
        ('l2', 'L2'),
        ('l3', 'L3'),
        ('l4', 'L4'),
        ('l5', 'L5')
    ], 'BOM Level')

    x_is_allocation = fields.Boolean('Phân bổ chi phí chung', default=False)
    x_price_line_ids = fields.One2many('production.cost.price', 'production_id', 'Chi phí')
    x_weight = fields.Float('Trọng lượng')
    x_shift = fields.Char('Ca')
    x_labor = fields.Many2many(comodel_name='hr.employee', relation='x_labor_hr_employee_mrp_production_rel', string="Nhân công")

    @api.onchange('bom_id')
    def _onchange_set_cost_price(self):
        try:
            values = []
            for line in self.bom_id.x_price_line_ids:
                vals = {
                    'account_debt_id': line.account_debt_id.id,
                    'account_credit_id': line.account_credit_id.id,
                    'price_unit': line.price_unit,
                    'amount': self.product_qty * line.price_unit,
                }
                values.append((0, 0, vals))
            self.x_price_line_ids = None
            self.x_price_line_ids = values
        except Exception as e:
            raise ValidationError(e)
    @api.onchange('bom_id')
    def _onchange_bom_set_level(self):
        try:
            if self.bom_id:
                self.x_level = self.bom_id.x_level
                self.x_is_allocation = self.bom_id.x_is_allocation
        except Exception as e:
            raise ValidationError(e)

    @api.model
    def create(self, vals):
        try:
            res = super(MrpProduction, self).create(vals)
            if not res.x_level:
                res.x_level = res.bom_id.x_level
                res.x_is_allocation = res.bom_id.x_is_allocation

            return res
        except Exception as e:
            raise ValidationError(e)
