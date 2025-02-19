from datetime import datetime

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _create_stock_moves_transfer(self, picking):
        moves = self.env['stock.move']
        for line in self:
            if line.quantity == 0:
                continue
            vals = line._prepare_stock_moves_transfer(picking)
            moves.sudo().create(vals)

    def _prepare_stock_moves_transfer(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        # if self.product_uom == self.product_id.product_colorcode_id.uom_id:
        #     x_qty_change = round(self.quantity_done)
        # else:
        #     x_qty_change = round(
        #         self.quantity_done * self.product_id.product_colorcode_id.product_change_type) if self.product_id.product_colorcode_id else 0
        vals = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            # 'x_lot_id': self.x_lot_id.id,
            # 'x_first_production_date': self.x_first_production_date,
            # 'x_product_kg_number': self.x_product_kg_number,
            # 'x_product_bin_number': self.x_product_bin_number,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.quantity,
            # 'x_qty_change': x_qty_change,
            'date': picking.scheduled_date,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'state': 'draft',
            'company_id': picking.company_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'origin': picking.name,
            'route_ids': (picking.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in picking.picking_type_id.warehouse_id.route_ids])] or []),
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
        }
        res.append(vals)
        return res
