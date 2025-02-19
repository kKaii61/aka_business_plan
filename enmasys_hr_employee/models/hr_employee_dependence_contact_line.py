from odoo import models, fields, _

DEPENDENT_CONTACT_GENDER = [
    ('male', "Male"),
    ('female', "Female"),
    ('other', "Other")
]


class HrEmployeeDependenceContactLine(models.Model):
    _name = "hr.employee.dependence.contact.line"
    _description = "Dependent Contact"

    # inverse_name
    x_hr_employee_id = fields.Many2one(comodel_name="hr.employee", string="Nhân viên")

    # each line
    x_dependent_contact_name = fields.Char(string="Họ và tên")
    x_dependent_contact_birthdate = fields.Date(string="Ngày sinh")
    x_dependent_contact_gender = fields.Selection(selection=DEPENDENT_CONTACT_GENDER,
                                                  string="Giới tính")
    x_dependent_contact_relationship_id = fields.Many2one(comodel_name="relatives.type", string="Quan hệ")
    x_dependent_contact_attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                                          string="File đính kèm")
    x_tax_number = fields.Char(string="Mã số thuế")
    x_dependent_nationality = fields.Char(string="Quốc tịch")
    x_dependent_reference_no = fields.Char(string="Quyển số")
    x_dependent_ward = fields.Char(string="Phường xã")
    x_dependent_district = fields.Char(string="Quận huyện")
    x_dependent_state = fields.Char(string="Thành phố")
    x_depend_from_date = fields.Date(string="Từ ")
    x_depend_to_date = fields.Date(string="Đến")
    x_identification_id = fields.Char('CCCD')

    def get_address(self):
        address_parts = [self.x_dependent_ward, self.x_dependent_district, self.x_dependent_state]
        return ', '.join([part for part in address_parts if part])
