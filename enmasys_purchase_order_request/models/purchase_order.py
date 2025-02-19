from odoo import api, fields, models, tools, SUPERUSER_ID


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'YCBG'),
        ('tp_approved', 'TP duyệt'),
        ('bod_approved', 'BOD duyệt'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def button_confirm(self):
        for order in self:
            if order.state == 'draft':
                order.state = 'tp_approved'
        return super().button_confirm()

    def button_tp_approved(self):
        for order in self:
            if order.state == 'tp_approved' and self.env.user.has_group(
                    'enmasys_purchase_order_request.group_purchase_order_tp'):
                order.state = 'bod_approved'

    def button_bod_approved(self):
        for order in self:
            if order.state == 'bod_approved' and self.env.user.has_group(
                    'enmasys_purchase_order_request.group_purchase_order_bod'):
                if order.state not in ['draft', 'bod_approved']:
                    continue
                order.order_line._validate_analytic_distribution()
                order._add_supplier_to_product()
                # Deal with double validation process
                if order._approval_allowed():
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
            return True

    def button_reject(self):
        for order in self:
            if order.state == 'tp_approved':
                order.state = 'draft'
            elif order.state == 'bod_approved':
                order.state = 'tp_approved'