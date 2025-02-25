from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ArchitectCommissionPercentage(models.Model):
    _name = 'architect.commission.percentage'
    _description = 'Phần trăm hoa hồng KTS'
    _rec_name = 'x_name'


    x_code_name = fields.Char(string="Mã code", required=True)
    x_name = fields.Char(string="Tên", required=True)
    x_discount_from = fields.Float(string="% Chiết khấu từ", required=True)
    x_discount_to = fields.Float(string="% Chiết khấu đến", required=True)
    x_commission = fields.Float(string="% Hoa hồng", required=True)

    @api.constrains('x_commission','x_discount_from', 'x_discount_to')
    def _check_discount_range(self):
        for record in self:
            if record.x_discount_from < 0 or record.x_discount_to > 100:
                raise ValidationError("Chiết khấu phải nằm trong khoảng từ 0% đến 100%.")

            if record.x_discount_from >= record.x_discount_to:
                raise ValidationError("Giá trị 'Chiết khấu từ' phải nhỏ hơn 'Chiết khấu đến'.")
            
            if record.x_commission <= 0:
                raise ValidationError("Giá trị của hoa hồng không nhận giá trị âm")

            # Kiểm tra xem có trùng lặp với khoảng khác không
            overlapping_records = self.search([
                ('id', '!=', record.id),  # Loại trừ chính nó khi cập nhật
                ('x_discount_from', '<', record.x_discount_to),
                ('x_discount_to', '>', record.x_discount_from),
            ])
            if overlapping_records:
                raise ValidationError("Khoảng chiết khấu đã tồn tại. Vui lòng chọn khoảng khác.")
