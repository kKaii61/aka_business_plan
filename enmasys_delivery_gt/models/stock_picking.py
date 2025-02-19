from odoo import api, fields, models, tools, SUPERUSER_ID, _
from lxml import etree
from odoo.exceptions import AccessError, ValidationError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_material_out = fields.Boolean(string='Phiếu xuất nguyên vật liệu')
    picking_out_id = fields.Many2one('stock.picking', string='Chứng từ nơi xuất nguyên VL')
    export_stock_material_count = fields.Integer(compute='compute_export_stock_material_count')
    commitment_date = fields.Datetime(string="Delivery Date")

    def compute_export_stock_material_count(self):
        for record in self:
            record.export_stock_material_count = self.env['stock.picking'].search_count(
                [('picking_out_id', '=', self.id)])



    def view_export_stock_material(self):
        self.ensure_one()
        export_stock_material = self.env['stock.picking'].search([('picking_out_id', '=', self.id)])
        val = {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu xuất vật liệu',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', export_stock_material.ids)],
            'context': "{'create': False}"
        }
        return val

    def action_create_export_stock_material(self):
        context = dict(self.env.context or {})
        context.update({
            'default_is_material_out': True,
            'default_picking_out_id': self.id,
            'restricted_picking_type_code': 'outgoing',
            'default_partner_id': self.partner_id.id if self.partner_id else None,
            'default_partner_address_id': self.partner_id.id if self.partner_id else None,
        })
        action = self.env["ir.actions.actions"]._for_xml_id("enmasys_delivery_gt.stock_picking_out_action")
        action['target'] = 'current'
        action['views'] = [(False, 'form')]
        action['context'] = context
        return action

    def action_create_tradition_delivery(self):
        self.check_rules_delivery()
        vals_delivery = {
            'partner_id': self.mapped('partner_id')[0].id if self.mapped('partner_id') else None,
            'partner_address_id': self.mapped('partner_id')[0].id if self.mapped('partner_id') else None,
            'picking_ids': self.ids,
        }
        delivery_id = self.env['tradition.delivery'].create(vals_delivery)
        form_view_id = self.env.ref('enmasys_delivery_gt.tradition_delivery_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': delivery_id.name,
            'view_mode': 'form',
            'res_model': 'tradition.delivery',
            'view_id': form_view_id,
            'res_id': delivery_id.id,
            'target': 'current',
        }

    def check_rules_delivery(self):
        check_partner = set(self.mapped('partner_id'))
        if len(check_partner) > 1:
            raise UserError('Bạn đang chọn nhiều khách hàng. Vui lòng chọn chung 1 khách hàng!')
        check_type_code = self.filtered(lambda rec: rec.picking_type_id.code != 'outgoing')
        if check_type_code:
            raise UserError('Bạn đang chọn phiếu xuất kho. Vui lòng chọn lại phiếu xuất kho!')
