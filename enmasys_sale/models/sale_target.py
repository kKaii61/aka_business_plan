from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date, time


class SaleTarget(models.Model):
    _name = "sale.target"
    _description = "Mục tiêu doanh số"

    business_plan_id = fields.Many2one("business.plan", string="Kế hoạch kinh doanh")
    # import_id = fields.Many2one('sale.target.import', 'Import ID')

    day = fields.Date(string="Day")
    wday = fields.Selection(
        [
            ("0", "Thứ Hai"),
            ("1", "Thứ Ba"),
            ("2", "Thứ Tư"),
            ("3", "Thứ Năm"),
            ("4", "Thứ Sáu"),
            ("5", "Thứ Bảy"),
            ("6", "Chủ Nhật"),
        ],
        string="Days of Week",
        compute="_compute_wday",
        store=True,
    )
    partner_group_id = fields.Many2one(
        "res.partner.group",
        string="Customer group",
        compute="_compute_partner_group_id",
        store=True,
    )
    partner_id = fields.Many2one("res.partner", string="Customer", required=True)

    target_revenue = fields.Float(string="Target")
    actual_revenue = fields.Float(
        string="Actual", compute="_compute_actual_revenue", store=True
    )
    year = fields.Integer(related="business_plan_id.year", store=True)
    rate_achieved = fields.Float(
        string="Rate Achieved", compute="_compute_rate_achieved", store=True
    )

    month = fields.Selection(
        [
            ("1", "Jan"),
            ("2", "Feb"),
            ("3", "Mar"),
            ("4", "Apr"),
            ("5", "May"),
            ("6", "Jun"),
            ("7", "Jul"),
            ("8", "Aug"),
            ("9", "Sep"),
            ("10", "Oct"),
            ("11", "Nov"),
            ("12", "Dec"),
        ],
        string="Month",
    )
    date_from = fields.Date(string="From date")
    date_to = fields.Date(string="To date")

    # =================== Added =========================================
    #
    #

    # từ store_id sang showroom_id
    user_id = fields.Many2one(
        "res.users", string="Employees", compute="_compute_user_id", store=True
    )

    showroom_id = fields.Many2one("hr.department", string="Showroom")
    member_ids = fields.Many2one(
        "hr.employee",
        string="Showroom members",
        compute="_compute_member_ids",
        store=True,
    )

    # Inventory
    brand_id = fields.Many2one("product.brand", string="brand")
    category_id = fields.Many2one("product.category", string="category")
    quantity_base_on_cat = fields.Float(string="Số lượng")

    # mục tiêu chọn theo năm/tháng
    target_profit = fields.Selection(
        [("by_month", "Profit By Month"), ("by_year", "Profit By Year")],
        string="Profit Target",
        required=True,
        default="by_month",
    )

    # chọn index năm (năm thứ 1, năm thứ 2, ...)
    index_year = fields.Integer(string="Năm thứ")
    # tháng trong năm index
    month_from = fields.Selection(
        [
            ("1", "Jan"),
            ("2", "Feb"),
            ("3", "Mar"),
            ("4", "Apr"),
            ("5", "May"),
            ("6", "Jun"),
            ("7", "Jul"),
            ("8", "Aug"),
            ("9", "Sep"),
            ("10", "Oct"),
            ("11", "Nov"),
            ("12", "Dec"),
        ],
        string="Từ tháng",
    )
    month_to = fields.Selection(
        [
            ("1", "Jan"),
            ("2", "Feb"),
            ("3", "Mar"),
            ("4", "Apr"),
            ("5", "May"),
            ("6", "Jun"),
            ("7", "Jul"),
            ("8", "Aug"),
            ("9", "Sep"),
            ("10", "Oct"),
            ("11", "Nov"),
            ("12", "Dec"),
        ],
        string="Đến tháng",
    )

    #
    #
    # =============================================================
    @api.depends("showroom_id")
    def _compute_user_id(self):
        for record in self:
            if record.showroom_id:
                # Get the first employee in the showroom
                first_employee = self.env["hr.employee"].search(
                    [("department_id", "=", record.showroom_id.id)], limit=1
                )
                record.user_id = first_employee.id if first_employee else False
            else:
                record.user_id = None

    @api.depends("showroom_id")
    def _compute_member_ids(self):
        for rc in self:
            if rc.showroom_id:
                # Get all employees in the selected showroom
                rc.member_ids = self.env["hr.employee"].search(
                    [("department_id", "=", rc.showroom_id.id)]
                )
            else:
                rc.member_ids = None

    @api.onchange("member_ids")
    def _onchange_member_ids(self):
        for rc in self:
            if rc.member_ids:
                rc.showroom_id = rc.member_ids.department_id
            else:
                rc.showroom_id = None

    @api.onchange("target_profit")
    def _onchange_target_profit(self):
        for rc in self:
            if rc.target_profit == "by_year":
                rc.month = None
                rc.date_from = None
                rc.date_to = None
            elif rc.target_profit == "by_month":
                rc.index_year = None
                rc.month_from = None
                rc.month_to = None
    @api.depends('target_revenue', 'actual_revenue')


    ######################################################################
    @api.onchange("month")
    def onchange_month(self):
        if self.month and self.year:
            month = int(self.month)
            year = self.year
            first_day = datetime(year, month, 1)
            # Cập nhật để xử lý tháng 12
            last_day = (
                datetime(year, month + 1, 1) - timedelta(days=1)
                if month < 12
                else datetime(year + 1, 1, 1) - timedelta(days=1)
            )
            self.date_from = first_day
            self.date_to = last_day

    @api.depends("partner_id")
    def _compute_partner_group_id(self):
        for record in self:
            if record.partner_id:
                record.partner_group_id = record.partner_id.partner_group_id
            else:
                record.partner_id = None

    @api.depends("partner_id")
    def _compute_user_id(self):
        for record in self:
            if record.partner_id:
                record.user_id = record.partner_id.user_id
            else:
                record.user_id = None

    @api.depends("day", "partner_id", "business_plan_id.status", "month")
    def _compute_actual_revenue(self):
        for record in self:
            if record.day:
                if record.business_plan_id.status == "confirm":
                    domain = [
                        ("invoice_date", ">=", datetime.combine(record.day, time.min)),
                        ("invoice_date", "<=", datetime.combine(record.day, time.max)),
                        ("state", "=", "posted"),
                    ]
                    if record.partner_id:
                        domain.append(("partner_id", "=", record.partner_id.id))
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
                    record.actual_revenue = invoice_total - refund_total

                elif record.month and record.year:
                    if record.business_plan_id.status == "confirm":
                        current_date = record.date_from
                        actual_revenue = 0
                        while current_date <= record.date_to:
                            if record.business_plan_id.status == "confirm":
                                domain = [
                                    (
                                        "invoice_date",
                                        ">=",
                                        datetime.combine(current_date, time.min),
                                    ),
                                    (
                                        "invoice_date",
                                        "<=",
                                        datetime.combine(current_date, time.max),
                                    ),
                                    ("state", "=", "posted"),
                                ]
                                if record.partner_id:
                                    domain.append(
                                        ("partner_id", "=", record.partner_id.id)
                                    )
                                domain_invoice = domain + [
                                    ("move_type", "=", "out_invoice")
                                ]
                                domain_refund = domain + [
                                    ("move_type", "=", "out_refund")
                                ]
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
                                actual_revenue += invoice_total - refund_total
                            current_date += timedelta(days=1)
                        record.actual_revenue = actual_revenue
                else:
                    record.actual_revenue = 0
            else:
                record.actual_revenue = 0

    @api.constrains("day", "year")
    def _constrains_day(self):
        for record in self:
            if record.day and record.year:
                if record.day.year != record.business_plan_id.year:
                    raise UserError(
                        _("Phải chọn ngày trong năm %s" % record.business_plan_id.year)
                    )

    @api.constrains("day", "partner_id", "user_id")
    def _constrains_sale_target(self):
        for record in self:
            if record.day:
                sale_targets = self.search(
                    [
                        ("business_plan_id", "=", record.business_plan_id.id),
                        ("day", "=", record.day),
                        ("id", "!=", record.id),
                    ]
                )
                if len(sale_targets) > 0:
                    msg = (
                        "Không cho phép trùng ngày kế hoạch mà có dữ liệu trống: Ngày %s"
                        % record.day
                    )
                    if not record.partner_id:
                        raise UserError(_(msg))
                    if not record.user_id:
                        raise UserError(_(msg))
                    if (
                        len(sale_targets.mapped("partner_id.id")) == 0
                        or record.partner_id.id in sale_targets.mapped("partner_id.id")
                    ) and (
                        len(sale_targets.mapped("user_id.id")) == 0
                        or record.user_id.id in sale_targets.mapped("user_id.id")
                    ):
                        raise UserError(_(msg))

    @api.depends("target_revenue", "actual_revenue")
    def _compute_rate_achieved(self):
        for record in self:
            record.rate_achieved = (
                record.actual_revenue / record.target_revenue * 100
                if record.target_revenue != 0
                else 0
            )
