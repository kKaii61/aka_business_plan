from odoo import api, fields, models, tools, SUPERUSER_ID

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "TP Duyệt"),
    ("approved", "BOD Duyệt"),
    # ("bod_approved", "BOD duyệt"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_group_employee_purchase_request = fields.Boolean(compute='compute_is_group_employee_purchase_request',
                                                        default=lambda self: self.env.user.has_group(
                                                            'enmasys_purchase_request_sercurity.group_employee_purchase_request'))

    def compute_is_group_employee_purchase_request(self):
        self.is_group_employee_purchase_request = self.env.user.has_group(
            'enmasys_purchase_request_sercurity.group_employee_purchase_request')

    def button_approved(self):
        for line in self.line_ids:
            if not line.partner_id:
                raise UserError("Bạn vui lòng nhập nhà cung cấp cho các dòng đơn hàng!")
        res = super(PurchaseRequest, self).button_approved()
        return res

    # def button_bod_approved(self):
    #     for rec in self:
    #         rec.state = 'bod_approved'

    def button_done(self):
        purchase_request_line_make_purchase_order_obj = self.env['purchase.request.line.make.purchase.order']
        partners = self.line_ids.mapped('partner_id')
        purchase_obj = self.env['purchase.order']
        for partner in partners:
            lines_supplier = self.line_ids.filtered(lambda line: line.partner_id == partner)
            vals_line = purchase_request_line_make_purchase_order_obj.get_items(lines_supplier.ids)
            purchase_draft = purchase_obj.search(
                [('state', '=', 'draft'), ('partner_id', '=', partner.id)],
                order='create_date desc',
                limit=1)
            if purchase_draft:
                purchase_request_line_make_purchase_order_new = purchase_request_line_make_purchase_order_obj.create({
                    'purchase_order_id': purchase_draft.id,
                    'item_ids': vals_line,
                    'supplier_id': partner.id,
                })
                purchase_request_line_make_purchase_order_new.make_purchase_order()
            else:
                purchase_request_line_make_purchase_order_new = purchase_request_line_make_purchase_order_obj.create({
                    'supplier_id': partner.id,
                    'item_ids': vals_line
                })
                purchase_request_line_make_purchase_order_new.make_purchase_order()
        res = super(PurchaseRequest, self).button_done()
        return res
