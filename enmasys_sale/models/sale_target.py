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
    partner_id = fields.Many2one("res.partner", string="Customer")

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
    user_id = fields.Many2one("res.users", string="Employees", store=True)

    showroom_id = fields.Many2one("hr.department", string="Showroom")

    # Inventory
    brand_id = fields.Many2one("product.brand", string="brand")
    category_id = fields.Many2one("product.category", string="category")
    quantity_base_on_cat = fields.Float(string="Số lượng")

    # chọn index năm (năm 2025, năm 2026, ...)
    # tháng trong năm index
    index_year = fields.Integer(string="Năm")
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

    target_profit = fields.Selection(
        related="business_plan_id.target_profit", string="Profit Target", readonly=True
    )
    be_included = fields.Boolean(required=True, default=True)

    #
    #
    # =============================================================

    @api.onchange("month_from", "month_to")
    def _onchange_month_range(self):
        """Show warning if month_from is greater than month_to in the UI."""
        if self.month_from and self.month_to:
            month_from = self.month_from
            if int(self.month_from) > int(self.month_to):
                # set back to previous values
                self.month_from = month_from
                return {
                    "warning": {
                        "title": "Giá trị không hợp lệ",
                        "message": "Từ tháng phải nhỏ hơn Đến tháng.",
                    }
                }

    @api.constrains("month", "date_from", "date_to")
    def _constrains_date_from_to_month(self):
        for rc in self:
            month_date_from = rc.date_from.month
            month_date_to = rc.date_to.month
            i_month = int(rc.month)
            if (month_date_from != i_month) or (month_date_to != i_month):
                raise UserError(f"Không nhập quá ngày trong tháng: {i_month}")

    # onchange
    @api.onchange("user_id")
    def _onchange_user_id(self):
        for rc in self:
            if rc.user_id:
                rc.showroom_id = rc.user_id.department_id
            else:
                rc.showroom_id = None

    @api.onchange("month")
    def onchange_month_bymonth(self):
        if self.business_plan_id.target_profit == "by_month":
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
                print(f"From month: {self.date_from} to {self.date_to}")
                print("\n=================================================\n")

    @api.onchange("index_year", "month_from")
    def _onchange_monthfrom_byyear(self):
        if self.business_plan_id.target_profit == "by_year":
            if self.index_year:
                if self.month_from:
                    if self.month_to:
                        month_from = int(self.month_from)
                        month_to = int(self.month_to)
                        year = self.index_year
                        first_day = datetime(year, month_from, 1)
                        last_day = (
                            datetime(year, month_to + 1, 1) - timedelta(days=1)
                            if month_to < 12
                            else datetime(year + 1, 1, 1) - timedelta(days=1)
                        )
                        self.date_from = first_day
                        self.date_to = last_day
                        print(f"From index_year: {self.date_from} to {self.date_to}")
                        print("\n=================================================\n")
                    else:
                        month = int(self.month_from)
                        self.month_to = self.month_from
                        year = self.index_year
                        first_day = datetime(year, month, 1)
                        last_day = (
                            datetime(year, month + 1, 1) - timedelta(days=1)
                            if month < 12
                            else datetime(year + 1, 1, 1) - timedelta(days=1)
                        )
                        self.date_from = first_day
                        self.date_to = last_day
                        print(f"From index_year: {self.date_from} to {self.date_to}")
                        print("\n=================================================\n")
                else:
                    self.month_from = False

    @api.onchange("index_year", "month_to")
    def _onchange_monthto_byyear(self):
        if self.business_plan_id.target_profit == "by_year":
            if self.index_year:
                if self.month_to:
                    if self.month_from:
                        month_from = int(self.month_from)
                        month_to = int(self.month_to)
                        year = self.index_year
                        first_day = datetime(year, month_from, 1)
                        last_day = (
                            datetime(year, month_to + 1, 1) - timedelta(days=1)
                            if month_to < 12
                            else datetime(year + 1, 1, 1) - timedelta(days=1)
                        )
                        self.date_from = first_day
                        self.date_to = last_day
                        print(f"From index_year: {self.date_from} to {self.date_to}")
                        print("\n=================================================\n")
                    else:
                        return {
                            "warning": {
                                "title": "Giá trị không hợp lệ",
                                "message": "Xin nhập Từ tháng!",
                            }
                        }
                else:
                    self.month_to = False

    #########################################

    @api.depends(
        "index_year", "date_from", "date_to", "user_id", "brand_id", "category_id"
    )
    def _compute_actual_revenue(self):
        for rc in self:
            if (
                rc.date_from
                and rc.date_to
                and rc.category_id
                and rc.brand_id
                and rc.user_id
            ):
                # reset search and actual revenue
                so_invoiced = None
                rc.actual_revenue = 0
                so_invoiced = self.env["sale.order.line"].search(
                    [
                        ("order_id.date_order", ">", rc.date_from),
                        ("order_id.date_order", "<", rc.date_to),
                        ("order_id.user_id", "=", rc.user_id.id),
                        ("product_id.product_tmpl_id.x_brand_id", "=", rc.brand_id.id),
                        (
                            "product_id.product_tmpl_id.categ_id",
                            "child_of",
                            rc.category_id.id,
                        ),
                        ("order_id.invoice_status", "=", "invoiced"),
                    ]
                )
                if so_invoiced:
                    for order in so_invoiced:
                        for line in order:
                            so_product_quantity = line.product_uom_qty
                            unit_price = line.price_unit
                            subtotal = line.price_subtotal
                            if rc.be_included:
                                rc.actual_revenue += subtotal
                else:
                    rc.actual_revenue = 0
                    so_invoiced = None
            else:
                rc.actual_revenue = 0

    @api.constrains("date_from", "date_to", "category_id")
    def _check_date_and_category(self):
        for record in self:
            # Get all child_categories
            child_categories = (
                self.env["product.category"]
                .search([("id", "child_of", record.category_id.id)])
                .ids
            )
            parent_categories = (
                self.env["product.category"]
                .search([("id", "parent_of", record.category_id.id)])
                .ids
            )
            # Check if category_id equal than date must not =
            same_category_records = self.env["sale.target"].search(
                [
                    ("id", "!=", record.id),
                    ("business_plan_id", "=", record.business_plan_id.id),
                    "|", # or between child and parent
                    ("category_id", "in", child_categories),
                    ("category_id", "in", parent_categories),
                ]
            )
            if same_category_records and any(
                (r.date_from == record.date_from and r.date_to == record.date_to)
                or (r.date_from <= record.date_to and r.date_to >= record.date_from)
                for r in same_category_records
            ):
                record.be_included = False
                raise UserError(
                    f"Nếu danh mục giống nhau, ngày bắt đầu và kết thúc không được giống nhau! hoặc danh mục hiện tại {record.category_id.name} là con hoặc cha của danh mục trước đó!"
                )

    @api.constrains("date_from")
    def _constrains_date_from(self):
        """Ensure Date_from are inputed"""
        for record in self:
            if record.date_from == False:
                raise UserError("Nhập Từ tháng!")

    @api.constrains("date_to")
    def _constrains_date_to(self):
        """Ensure Date_to are inputed"""
        for record in self:
            if record.date_to == False:
                raise UserError("Nhập Đến tháng!")

    @api.constrains("month_from", "month_to")
    def _check_month_range(self):
        """Ensure that month_from is always smaller than month_to."""
        for record in self:
            if record.month_from and record.month_to:
                if int(record.month_from) > int(record.month_to):
                    raise ValidationError("Từ tháng phải nhỏ hơn Đến tháng.")

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
                (record.actual_revenue / record.target_revenue)
                if record.target_revenue != 0
                else 0
            )
