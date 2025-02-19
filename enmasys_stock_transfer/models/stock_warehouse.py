from odoo import models, fields, api, _, SUPERUSER_ID


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_location_transfer_id = fields.Many2one('stock.location', 'Điểm trung chuyển',
                                             domain=[('active', '=', True), ('usage', '=', 'transit')], index=True)

    def _get_locations_values(self, vals, code=False):
        sub_locations = super(StockWarehouse, self)._get_locations_values(vals, code)
        code = vals.get('code') or code or ''
        code = code.replace(' ', '').upper()
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        sub_locations.update({
            'x_location_transfer_id': {
                'name': _('DC'),
                'active': True,
                'usage': 'transit',
                'barcode': self._valid_barcode(code + '-TRANSFER', company_id)
            },
        })
        return sub_locations
