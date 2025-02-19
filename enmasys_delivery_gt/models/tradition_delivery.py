from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class TraditionDelivery(models.Model):
    _name = "tradition.delivery"
    _description = "Tradition Delivery"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Số chứng từ', default=lambda self: _('New'), readonly=True)
    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    partner_address_id = fields.Many2one('res.partner', 'Địa chỉ giao hàng')
    date = fields.Date(string='Ngày chứng từ', default=fields.Date.today)
    partner_worker_ids = fields.Many2many('res.partner','tradition_delivery_res_partner_rel', string='Thợ')
    picking_ids = fields.Many2many('stock.picking', 'tradition_delivery_stock_picking_rel', string='Phiếu xuất kho')
    date_delivery_start = fields.Datetime(string='Ngày bắt đầu giao')
    unit_delivery_id = fields.Many2one('res.partner', string='Đơn vị vận chuyển')
    employee_delivery_id = fields.Many2one('res.partner', string='Nhân viên vận chuyển')
    date_delivery_end = fields.Datetime(string='Ngày giao thành công')
    state = fields.Selection([
        ('draft', 'Mới'),
        ('delivery', 'Đang giao'),
        ('done', 'Thành công'),
        ('cancel', 'Hủy')],
        string='Trạng thái', default='draft')
    date_start = fields.Datetime(string='Ngày từ')
    date_end = fields.Datetime(string='Ngày đến')


    def check_sequence(self, date):
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'tradition.delivery.sequence')])

        val = []
        for line in sequence.date_range_ids:
            if line.date_from <= date <= line.date_to:
                val.append(line)
        if val:
            return True
        else:
            return False

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            time = datetime.now().date()
            if self.check_sequence(date=time) == False:
                sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'tradition.delivery.sequence')])
                value = {
                    'sequence_id': sequence.id,
                    'date_from': datetime.now().date(),
                    'date_to': datetime.now().date(),
                    'number_next_actual': 1

                }
                self.env['ir.sequence.date_range'].sudo().create(value)
            vals['name'] = self.env['ir.sequence'].next_by_code('tradition.delivery.sequence',
                                                                sequence_date=datetime.now().date()) or _('New')
        result = super(TraditionDelivery, self).create(vals)
        return result

    def button_delivery(self):
        for rec in self:
            rec.state = 'delivery'
            rec.date_delivery_start = datetime.now()

    def button_done(self):
        for rec in self:
            rec.state = 'done'
            rec.date_delivery_end = datetime.now()

    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'
