from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InheritHrEmployee(models.Model):
    _inherit = "hr.employee"

    # new
    x_all_subordinated_employee_ids = fields.Many2many(
        comodel_name="hr.employee", string="All subordinated employees",
        relation="superior_subordinate_rel", column1="superior_id", column2="subordinate_id",
        compute="_compute_x_all_subordinated_employee_ids")

    def get_all_directly_subordinates(self):
        try:
            superior_employee = self

            direct_subordinates = superior_employee.child_ids
            for direct_subordinate in superior_employee.child_ids:
                direct_subordinates += direct_subordinate.child_ids
            return direct_subordinates
        except Exception as e:
            raise ValidationError(e)

    def get_all_subordinates(self):
        try:
            superior_employee = self
            all_subordinates = superior_employee.get_all_directly_subordinates()
            for subordinate in superior_employee.child_ids:
                all_subordinates += subordinate.get_all_subordinates()
            return all_subordinates
        except Exception as e:
            raise ValidationError(e)

    def _compute_x_all_subordinated_employee_ids(self):
        try:
            for employee in self:
                employee.x_all_subordinated_employee_ids = [
                    subordinate.id for subordinate in employee.get_all_subordinates()]
        except Exception as e:
            raise ValidationError(e)
