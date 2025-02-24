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

    so_invoiced = fields.One2many("sale.order.line", compute="_compute_so_invoiced")

    target_profit = fields.Selection(
        related="business_plan_id.target_profit", string="Profit Target", readonly=True
    )

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

    # compute

    # onchange
    @api.onchange("user_id")
    def _onchange_user_id(self):
        for rc in self:
            if rc.user_id:
                rc.showroom_id = rc.user_id.department_id
            else:
                rc.showroom_id = None

    @api.onchange("user_id", "brand_id")
    def _onchange_user_brand_id(self):
        for rc in self:
            if rc.user_id:
                orders = self.env["sale.order"].search(
                    [("user_id", "=", self.user_id.id)]
                )
                print("\n==========  Employee  =================")
                print(orders.mapped("name"))
                for order in orders:
                    for line in order.order_line:
                        product = line.product_id
                        product_id = product.id
                        product_name = product.name
                        invoice_status = line.invoice_status
                        unit_price = line.price_unit
                        brand_name = (
                            product.product_tmpl_id.x_brand_id.name
                            if product.product_tmpl_id.x_brand_id
                            else "No Brand"
                        )
                        print(
                            f"({invoice_status}) Product: {product_name}: {product_id} - Price: {unit_price} - Brand: {brand_name} - Mem: {rc.user_id.name}"
                        )
                print("\n===========================")

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

    @api.onchange('index_year',"month_from")
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

    @api.onchange('index_year',"month_to")
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

    #########################################

    @api.depends('index_year','date_from', 'date_to', "user_id", "brand_id", "category_id")
    def _compute_actual_revenue(self):
        for rc in self:
            if (
                rc.date_from
                and rc.date_to
                and rc.category_id
                and rc.brand_id
                and rc.user_id
                and rc.business_plan_id.target_profit == "by_month"
            ):
                # reset search and actual revenue
                rc.so_invoiced = None
                rc.actual_revenue = 0
                rc.so_invoiced = self.env["sale.order.line"].search(
                    [
                        ("order_id.date_order", ">", rc.date_from),
                        ("order_id.date_order", "<", rc.date_to),
                        ("order_id.user_id", "=", rc.user_id.id),
                        ("product_id.product_tmpl_id.x_brand_id", "=", rc.brand_id.id),
                        ("product_id.product_tmpl_id.categ_id", "child_of", rc.category_id.id),
                        ("order_id.invoice_status", "=", "invoiced"),
                    ]
                )
                if rc.so_invoiced:
                    for order in rc.so_invoiced:
                        for line in order:
                            # rc.actual_revenue = 0
                            product = line.product_id
                            product_id = product.id
                            product_name = product.name
                            so_product_quantity = line.product_uom_qty
                            unit_price = line.price_unit
                            categ = product.categ_id
                            status = line.invoice_status
                            brand_name = (
                                product.product_tmpl_id.x_brand_id.name
                                if product.product_tmpl_id.x_brand_id
                                else "No Brand"
                            )
                            rc.actual_revenue += so_product_quantity * unit_price
                else:
                    rc.actual_revenue = 0
                    rc.so_invoiced = None
            elif (rc.date_from
                and rc.date_to
                and rc.category_id
                and rc.brand_id
                and rc.user_id
                and rc.business_plan_id.target_profit == "by_year"):
                # reset search and actual revenue
                rc.so_invoiced = None
                rc.actual_revenue = 0
                rc.so_invoiced = self.env["sale.order.line"].search(
                    [
                        ("order_id.date_order", ">", rc.date_from),
                        ("order_id.date_order", "<", rc.date_to),
                        ("order_id.user_id", "=", rc.user_id.id),
                        ("product_id.product_tmpl_id.x_brand_id", "=", rc.brand_id.id),
                        ("product_id.product_tmpl_id.categ_id", "child_of", rc.category_id.id),
                        ("order_id.invoice_status", "=", "invoiced"),
                    ]
                )
                if rc.so_invoiced:
                    for order in rc.so_invoiced:
                        for line in order:
                            # rc.actual_revenue = 0
                            product = line.product_id
                            product_id = product.id
                            product_name = product.name
                            so_product_quantity = line.product_uom_qty
                            unit_price = line.price_unit
                            categ = product.categ_id
                            status = line.invoice_status
                            brand_name = (
                                product.product_tmpl_id.x_brand_id.name
                                if product.product_tmpl_id.x_brand_id
                                else "No Brand"
                            )
                            rc.actual_revenue += so_product_quantity * unit_price
                else:
                    rc.actual_revenue = 0
                    rc.so_invoiced = None
            else:
                rc.actual_revenue = 0

    # @api.onchange("so_invoiced", "user_id", "brand_id", "category_id")
    # def onchange_actual_revenue(self):
    #     for rc in self:
    #         if rc.so_invoiced:
    #             for order in rc.so_invoiced:
    #                 for line in order:
    #                     rc.actual_revenue = 0
    #                     product = line.product_id
    #                     product_id = product.id
    #                     product_name = product.name
    #                     so_product_quantity = line.product_uom_qty
    #                     unit_price = line.price_unit
    #                     categ = product.categ_id
    #                     status = line.invoice_status
    #                     brand_name = (
    #                         product.product_tmpl_id.x_brand_id.name
    #                         if product.product_tmpl_id.x_brand_id
    #                         else "No Brand"
    #                     )
    #                     rc.actual_revenue += so_product_quantity * unit_price
    #                     print(product_id)
    #                     print(product_name)
    #                     print(so_product_quantity)
    #                     print(unit_price)
    #                     print(categ)
    #                     print(status)
    #                     print(brand_name)

    ##################################

    # @api.depends("day", "partner_id", "business_plan_id.status", "month")
    # def _compute_actual_revenue(self):
    #     for record in self:
    #         if record.day:
    #             if record.business_plan_id.status == "confirm":
    #                 domain = [
    #                     ("invoice_date", ">=", datetime.combine(record.day, time.min)),
    #                     ("invoice_date", "<=", datetime.combine(record.day, time.max)),
    #                     ("state", "=", "posted"),
    #                 ]
    #                 if record.partner_id:
    #                     domain.append(("partner_id", "=", record.partner_id.id))
    #                     domain_invoice = domain + [("move_type", "=", "out_invoice")]
    #                     domain_refund = domain + [("move_type", "=", "out_refund")]
    #                     invoice_total = sum(
    #                         self.env["account.move"]
    #                         .search(domain_invoice)
    #                         .mapped("amount_untaxed")
    #                     )
    #                     refund_total = sum(
    #                         self.env["account.move"]
    #                         .search(domain_refund)
    #                         .mapped("amount_untaxed")
    #                     )
    #                     record.actual_revenue = invoice_total - refund_total
    #             elif record.month and record.year:
    #                 if record.business_plan_id.status == "confirm":
    #                     current_date = record.date_from
    #                     actual_revenue = 0
    #                     while current_date <= record.date_to:
    #                         if record.business_plan_id.status == "confirm":
    #                             domain = [
    #                                 (
    #                                     "invoice_date",
    #                                     ">=",
    #                                     datetime.combine(current_date, time.min),
    #                                 ),
    #                                 (
    #                                     "invoice_date",
    #                                     "<=",
    #                                     datetime.combine(current_date, time.max),
    #                                 ),
    #                                 ("state", "=", "posted"),
    #                             ]
    #                             if record.partner_id:
    #                                 domain.append(
    #                                     ("partner_id", "=", record.partner_id.id)
    #                                 )
    #                             domain_invoice = domain + [
    #                                 ("move_type", "=", "out_invoice")
    #                             ]
    #                             domain_refund = domain + [
    #                                 ("move_type", "=", "out_refund")
    #                             ]
    #                             invoice_total = sum(
    #                                 self.env["account.move"]
    #                                 .search(domain_invoice)
    #                                 .mapped("amount_untaxed")
    #                             )
    #                             refund_total = sum(
    #                                 self.env["account.move"]
    #                                 .search(domain_refund)
    #                                 .mapped("amount_untaxed")
    #                             )
    #                             actual_revenue += invoice_total - refund_total
    #                         current_date += timedelta(days=1)
    #                     record.actual_revenue = actual_revenue
    #             else:
    #                 record.actual_revenue = 0
    #         else:
    #             record.actual_revenue = 0

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
