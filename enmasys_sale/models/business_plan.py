from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from lxml import etree
from datetime import datetime, time


class BusinessPlan(models.Model):
    _name = "business.plan"
    _description = "Kế hoạch kinh doanh"
    _rec_name = "name"

    target_profit = fields.Selection(
        [("by_month", "Profit By Month"), ("by_year", "Profit By Year")],
        string="Profit Target",
        required=True,
        default="by_month",
    )
    ##
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,  # Default to current company
    )
    ##
    is_user = fields.Boolean(compute="compute_is_user")
    name = fields.Char(string="Name", required=True)
    year = fields.Integer(string="Year", required=True, default=fields.Date.today().year)
    actual_revenue = fields.Float(
        string="Actual", compute="_compute_actual_revenue", store=True
    )
    target_revenue = fields.Float(
        string="Target", compute="_compute_target_revenue", store=True
    )
    status = fields.Selection(
        [("new", "New"), ("confirm", "Confirm")], string="State", default="new"
    )
    sale_target_ids = fields.One2many(
        "sale.target", "business_plan_id", string="Sales target"
    )
    sale_target_count = fields.Integer(compute="_compute_sale_target_count")
    total_annual_revenue = fields.Float(
        string="Total annual revenue", compute="_compute_total_annual_revenue"
    )

    

    def action_import(self):
        vals = {
            'business_plan_id': self.id
        }
        res = self.env['sale.target.import'].create(vals)
        return {
            'name': 'Record Form View',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.target.import',
            'view_mode': 'form',
            'res_id': res.id,
            'target': 'current',
        }

    # ========================= API =========================
    #
    #

    @api.constrains('year')
    def _constrains_year(self):
        """Ensure that year are inputed"""
        for record in self:
            if record.year == False:
                raise UserError("Nhập năm của dự án kinh doanh")

    @api.depends("sale_target_ids.actual_revenue")
    def _compute_actual_revenue(self):
        for record in self:
            if record.sale_target_ids:
                record.actual_revenue = sum(
                    record.sale_target_ids.mapped("actual_revenue")
                )

    @api.depends("sale_target_ids.target_revenue")
    def _compute_target_revenue(self):
        for record in self:
            if record.sale_target_ids:
                record.target_revenue = sum(
                    record.sale_target_ids.mapped("target_revenue")
                )

    @api.onchange('target_profit')
    def _onchange_target_profit(self):
        for rc in self:
            if rc.sale_target_ids and rc.target_profit:
                if rc.target_profit == "by_year":
                    rc.sale_target_ids.month = False
                    rc.sale_target_ids.date_from = False
                    rc.sale_target_ids.date_to = False
                    print("From onchange: target_profit")
                elif rc.target_profit == "by_month":
                    rc.sale_target_ids.index_year = False
                    rc.sale_target_ids.month_from = False
                    rc.sale_target_ids.month_to = False
                    print("From onchange: target_profit")

    #
    #
    #  ==========================================================

    # ========================= COMPUTE =========================
    #
    #
    def _compute_sale_target_count(self):
        self.sale_target_count = len(self.sale_target_ids)

    def compute_is_user(self):
        for record in self:
            if record.sale_target_ids:
                record.action_update_actual_revenue_sale_target()
            record.is_user = True

    def _compute_total_annual_revenue(self):
        for record in self:
            if record.status == "confirm":
                domain = [
                    (
                        "invoice_date",
                        ">=",
                        datetime.combine(datetime(record.year, 1, 1), time.min),
                    ),
                    (
                        "invoice_date",
                        "<=",
                        datetime.combine(
                            datetime(record.year, 12, 31), time.max
                        ).replace(year=record.year),
                    ),
                    ("state", "=", "posted"),
                ]
                domain_invoice = domain + [("move_type", "=", "out_invoice")]
                domain_refund = domain + [("move_type", "=", "out_refund")]
                invoice_total = sum(
                    self.env["account.move"]
                    .search(domain_invoice)
                    .mapped("amount_untaxed")
                )
                refund_total = sum(
                    self.env["account.move"]
                    .search(domain_refund)
                    .mapped("amount_untaxed")
                )
                record.total_annual_revenue = invoice_total - refund_total
            else:
                record.total_annual_revenue = 0

    #
    #
    #  ==================================================
    def action_view_sale_target(self):
        return {
            "name": _("Mục tiêu doanh số"),
            "type": "ir.actions.act_window",
            "res_model": "sale.target",
            "views": [
                [self.env.ref("enmasys_sale.sale_target_view_tree").id, "list"],
                [self.env.ref("enmasys_sale.sale_target_view_form").id, "form"],
            ],
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("business_plan_id", "=", self.id)],
        }

    def action_confirm(self):
        for record in self:
            record.update({"status": "confirm"})

    def action_update_actual_revenue_sale_target(self):
        for record in self:
            for line in record.sale_target_ids:
                line._compute_actual_revenue()

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     print('view')
    #     return super(BusinessPlan, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
