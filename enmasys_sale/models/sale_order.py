from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import dateutil.parser


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_architect_introduction = fields.Boolean(string="Kiến trúc sư giới thiệu")
    x_architect_name = fields.Many2one('hr.employee', string="Kiến trúc sư")
    discount_percentage = fields.Float(string="Chiết khấu", compute="_compute_discount_percentage", store=True)
    x_architect_commission_percentage = fields.Float(string="Phần trăm hoa hồng KTS", compute="_get_commission_percentage", store=True)
    
    x_sm_requested = fields.Boolean(string="SM đã nhận yêu cầu", default=False)
    x_mail_sent = fields.Boolean(string="Email Sent", default=False)

    def action_quotation_send(self):
        """ Override action_quotation_send to mark x_mail_sent as True """
        res = super(SaleOrder, self).action_quotation_send()
        self.write({'x_mail_sent': True})
        return res


    state = fields.Selection([
        ('draft', "Quotation"),
        ('sent', "Quotation Sent"),
        ('sent_sm_approved', "SM Sent"),
        ('sm_approved', "SM Approved"),
        # ('bm_approved', "BM Approved"),
        ('sale', "Sales Order"),
        ('cancel', "Cancelled")
    ], string="Status", tracking=True, default='draft')


    def action_send_mail(self):
        """ Gửi email và chuyển trạng thái sang 'sent' nếu có kiến trúc sư giới thiệu """
        res = super(SaleOrder, self).action_quotation_send()
        for order in self:
            if order.x_architect_introduction:
                order.state = 'sent'
        return res
    def action_request_sm(self):
        """ chuyển từ trạng thái báo giá sang sm_approved"""
        for order in self:
            if order.state == "sent":
                order.state = 'sent_sm_approved'

    def action_sm_approve(self):
        """ Chuyển trạng thái từ 'sm_approved' sang 'bm_approved' """
        for order in self:
            if order.state == 'sent_sm_approved':
                order.state = 'sm_approved'

    def action_bm_approve(self):
        """ Chuyển trạng thái từ 'bm_approved' sang 'báo giá đã gửi' """
        for order in self:
            if order.state == 'sm_approved':
                order.state = 'bm_approved'

    def action_revert_to_sent(self):
        """ Quay lại trạng thái 'sent' """
        for order in self:
            if order.state == 'sm_approved':
                order.state = 'sent'

    def action_revert_to_sm_approved(self):
        """ Quay lại trạng thái 'sm_approved' """
        for order in self:
            if order.state == 'bm_approved':
                order.state = 'sm_approved'
            elif order.state == 'sm_approved':
                order.state = 'sent_sm_approved'
            elif order.state=='sent_sm_approved':
                order.state = 'sent'

    def action_cancel_order(self):
        """ Chuyển trạng thái sang 'cancel' """
        self.write({'state': 'cancel'})

    def _can_be_confirmed(self):
        self.ensure_one()
        return self.state in {'draft', 'sent','sm_approved'}
    #####################################################################################
    @api.depends('order_line.discount')
    def _compute_discount_percentage(self):
        """ Lấy giá trị % chiết khấu lớn nhất từ các dòng sản phẩm """
        for order in self:
            if order.order_line:
                order.discount_percentage = max(order.order_line.mapped('discount'))
            else:
                order.discount_percentage = 0.0
    #####################################################################caculator architect commission percentage
    
    @api.depends('discount_percentage')
    def _get_commission_percentage(self):
        for order in self:
            conmission = self.env['architect.commission.percentage'].search([
                ('x_discount_from','<',order.discount_percentage),
                ('x_discount_to','>=',order.discount_percentage)
            ], limit=1)
            order.x_architect_commission_percentage = conmission.x_commission or 0
            
    #Tính chiết khấu
    def compute_kts_commission(self):
        for order in self:
            if order.x_architect_introduction and order.x_architect_commission_percentage:
                commission_rate = order.x_architect_commission_percentage.percentage / 100
                order.amount_kts_commission = order.amount_total * commission_rate
    amount_kts_commission = fields.Monetary(
        string="Hoa hồng KTS", compute="compute_kts_commission", store=True
    )
    #

    @api.model
    def default_get(self, fields):
        defaults = super(SaleOrder, self).default_get(fields)
        user_current = self.env.user
        if user_current.property_warehouse_id:
            defaults['warehouse_id'] = user_current.property_warehouse_id.id
        return defaults

    architect_partner_id = fields.Many2one('res.partner', string='Kiến trúc sư',
                                           domain=[('x_group_id.code', '=', 'KTS')])

    def action_view_purchase_request(self):
        purchase_request_list = self.env['purchase.request'].search([('origin', '=', self.name)])
        val = {
            'type': 'ir.actions.act_window',
            'name': 'Yêu cầu mua hàng',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'purchase.request',
            'domain': [('id', 'in', purchase_request_list.ids)],
            'context': "{'create': False}"
        }
        return val

    def compute_purchase_request_count(self):
        for record in self:
            record.purchase_request_count = self.env['purchase.request'].search_count([('origin', '=', self.name)])

    purchase_request_count = fields.Integer(compute='compute_purchase_request_count')

    def get_report_sale_order_line(self):
        merge_dict_product = {}
        dict_product_print = {}
        new_dict_product = {}
        for rec in self:
            for line in rec.order_line:
                key = str(line.product_id.id) + '_' + str(line.price_unit) + 'true'
                if key in dict_product_print:
                    dict_product_print[key]['product_uom_qty'] += line.product_uom_qty
                    dict_product_print[key]['price_subtotal'] += line.price_subtotal
                else:
                    get_name_variant = []
                    product_variant_value = rec.get_variant_value(line)
                    if product_variant_value:
                        product_variant = rec.env['product.template.attribute.value'].browse(product_variant_value)
                        for product_template_variant_value in product_variant:
                            get_name_variant.append(product_template_variant_value.name)
                    dict_product_print[key] = {'product_name': line.product_id.name,
                                               'product_uom': line.product_uom.name,
                                               'product_uom_qty': line.product_uom_qty,
                                               'price_unit': line.price_unit,
                                               'discount': line.discount,
                                               'price_subtotal': line.price_subtotal,
                                               'x_product_template_variant_value_ids': ','.join(
                                                   get_name_variant) if get_name_variant else '',
                                               'print': True,
                                               'number': 0
                                               }
        merge_dict_product.update(dict_product_print)
        number = 0
        for dict in merge_dict_product:
            if merge_dict_product[dict]['product_uom_qty'] != 0:
                new_dict_product[dict] = merge_dict_product[dict]
        for dict_new in new_dict_product:
            number += 1
            merge_dict_product[dict_new]['number'] = number
        return new_dict_product

    def get_variant_value(self, line):
        if line.product_id.product_template_variant_value_ids:
            return line.product_id.product_template_variant_value_ids.ids
        else:
            return None

    def _get_date_order(self):
        for rec in self:
            datetimes = str(rec.date_order)
            date = dateutil.parser.parse(datetimes).date()
            return date

    def sum_quantity_line(self):
        for rec in self:
            vals = []
            for line in rec.order_line:
                vals.append(line.product_uom_qty)
            return '{:,.0f}'.format(sum(vals))

    def _get_sum_price_subtotal(self):
        for rec in self:
            vals = []
            for line in rec.order_line:
                vals.append(line.price_subtotal)
            return '{:,.0f}'.format(sum(vals))

    def _get_amount_untaxed(self):
        for rec in self:
            return '{:,.0f}'.format(rec.amount_untaxed)

    def _get_amount_total(self):
        for rec in self:
            return '{:,.0f}'.format(rec.amount_total)

    def _convert_to_tax_base_line_dict_report(self, line, tax, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=line.order_id.partner_id,
            currency=line.order_id.currency_id,
            product=line.product_id,
            taxes=tax,
            price_unit=line.price_unit,
            quantity=line.product_uom_qty,
            discount=line.discount,
            price_subtotal=line.price_subtotal,
            **kwargs,
        )

    def get_amount_tax(self, line, tax):
        """
        Compute the amounts of the SO line.
        """

        tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
            self._convert_to_tax_base_line_dict_report(line=line, tax=tax)
        ])
        totals = list(tax_results['totals'].values())[0]
        # amount_untaxed = totals['amount_untaxed']
        amount_tax = totals['amount_tax']
        return amount_tax

    def _data_report_tax(self):
        for rec in self:
            tax_list = []
            taxes = rec.order_line.mapped('tax_id')
            for tax in taxes:
                lines = rec.order_line.filtered(lambda line: tax in line.tax_id)
                sum_tax = []
                for line in lines:
                    sum_tax.append(self.get_amount_tax(line=line, tax=tax))
                tax_list.append({
                    'name': tax.tax_group_id.name,
                    'total': sum(sum_tax),
                })
            return tax_list
