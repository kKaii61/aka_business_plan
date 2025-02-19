from datetime import datetime

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict, OrderedDict

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_warehouse(self):
        warehouses = self.env['stock.warehouse'].search([('view_location_id', 'parent_of', self.ids)])
        warehouses = warehouses.sorted(lambda w: w.view_location_id.parent_path, reverse=True)
        view_by_wh = OrderedDict((wh.view_location_id.id, wh.id) for wh in warehouses)
        self.warehouse_id = False
        for loc in self:
            if not loc.parent_path:
                continue
            path = set(int(loc_id) for loc_id in loc.parent_path.split('/')[:-1])
            for view_location_id in view_by_wh:
                if view_location_id in path:
                    return view_by_wh[view_location_id]