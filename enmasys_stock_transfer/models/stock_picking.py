from datetime import datetime

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse destination', copy=False, tracking=True)
    x_is_transfer_incoming = fields.Boolean('Là phiếu nhận điều chuyển', default=False, copy=False)

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for rc in self:
            if rc.picking_type_code == 'internal' and rc.x_warehouse_id and not rc.x_is_transfer_incoming:
                rc._create_picking_transfer()
        return res

    def copy(self, default=None):
        if self.x_is_transfer_incoming:
            raise UserError(_('Đây là phiếu nhận điều chuyển. Bạn không thể nhân bản'))
        return super(StockPicking, self).copy(default)

    def do_unreserve(self):
        for rc in self:
            if rc.x_is_transfer_incoming:
                raise UserError(_('Đây là phiếu nhận điều chuyển. Bạn không thể hủy giữ hàng'))
        return super(StockPicking, self).do_unreserve()

    def action_cancel(self):
        for rc in self:
            if rc.x_is_transfer_incoming:
                raise UserError(_('Đây là phiếu nhận điều chuyển. Bạn không thể hủy'))
        return super(StockPicking, self).action_cancel()

    def unlink(self):
        for rc in self:
            if rc.x_is_transfer_incoming:
                raise UserError(_('Đây là phiếu nhận điều chuyển. Bạn không thể xóa'))
        return super(StockPicking, self).unlink()

    def _create_picking_transfer(self):

        domain = [('warehouse_id', '=', self.x_warehouse_id.id), ('code', '=', 'internal'),
                  ('default_location_dest_id', '=', self.x_warehouse_id.lot_stock_id.id)]
        picking_type_id = self.env['stock.picking.type'].sudo().search(domain, order='id desc', limit=1)
        if not picking_type_id:
            raise UserError(_('Kho %s chưa có điều chuyển nhận hàng! Vui lòng liên hệ quản trị viên') % self.x_warehouse_id.name)
        stock_picking = self.env['stock.picking']
        vals = self._prepare_picking_transfer(picking_type_id.id)
        picking = stock_picking.sudo().create(vals)
        self.move_ids_without_package._create_stock_moves_transfer(picking)
        picking.sudo().action_confirm()
        picking.sudo().action_assign()
        for move in self.move_ids_without_package:
            for line in move.move_line_ids:
                line.quantity = move.product_uom_qty

    @api.model
    def _prepare_picking_transfer(self, picking_type_id):
        return {
            'picking_type_id': picking_type_id,
            'date': datetime.now(),
            'origin': self.name,
            'location_dest_id': self.x_warehouse_id.lot_stock_id.id,
            'location_id': self.location_dest_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            # 'driver_name': self.driver_name,
            # 'call_their': self.call_their,
            # 'license_plates': self.license_plates,
            # 'reason_shipment': self.reason_shipment,
            # 'note_so': self.note_so,
            # 'general_note': self.general_note,
            # 'x_output_format': self.x_output_format,
            'x_is_transfer_incoming': True,
            'x_warehouse_id': self.location_id.get_warehouse(),
        }
