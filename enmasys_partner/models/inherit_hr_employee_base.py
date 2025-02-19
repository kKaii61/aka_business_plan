import logging

from odoo import models, _

from ..partner_classes import PartnerException as PartnerEx
_logger = logging.getLogger(__name__)


class InheritHrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def _create_work_contacts(self):
        return self

    def generate_work_contact_raw_vals(self, partner_group_code):
        try:
            self.ensure_one()
            work_contact_raw_vals = dict()  # <res.partner> vals
            employee_customer_group = self.env['res.partner.group'].search([
                ('code', '=', partner_group_code)
            ], limit=1)
            if not employee_customer_group:
                partner_group_with_code_msg = _("Partner-Group with code")
                problem_msg = _("is not existed in System. Please Check again.")
                PartnerEx.raise_exception_directly(
                    message="%(partner_group_with_code)s %(group_code)s %(problem)s" % {
                        'partner_group_with_code': partner_group_with_code_msg,
                        'group_code': partner_group_code,
                        'problem': problem_msg
                    }, exception_type='user_error')
            work_contact_raw_vals['company_type'] = 'person'
            work_contact_raw_vals['name'] = self.name
            work_contact_raw_vals['email'] = self.work_email
            work_contact_raw_vals['mobile'] = self.mobile_phone
            work_contact_raw_vals['phone'] = self.work_phone
            work_contact_raw_vals['company_name'] = self.company_id.name
            work_contact_raw_vals['lang'] = self.lang
            work_contact_raw_vals['company_id'] = self.company_id.id
            work_contact_raw_vals['street'] = self.private_street
            work_contact_raw_vals['street2'] = self.private_street2
            work_contact_raw_vals['user_id'] = self.user_id.id
            work_contact_raw_vals['x_group_id'] = employee_customer_group.id
            return work_contact_raw_vals
        except Exception as e:
            PartnerEx(exception=e).catch_and_handle_exception()

    @classmethod
    def _generate_client_action(cls, message, msg_type='success'):
        try:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': msg_type,
                    'message': message,
                }
            }
        except Exception as e:
            PartnerEx(exception=e).catch_and_handle_exception()

    def create_work_contact(self):
        try:
            if any(employee.work_contact_id for employee in self):
                return self._generate_client_action(
                    message=_("Some employee already have a work contact."),
                    msg_type='warning')
            work_contacts = self.env['res.partner'].create([
                employee.generate_work_contact_raw_vals(partner_group_code="NV") for employee in self
            ])
            for employee, work_contact in zip(self, work_contacts):
                employee.work_contact_id = work_contact
            return self._generate_client_action(
                    message=_("Work-Contact is generated successfully."))
        except Exception as e:
            PartnerEx(exception=e).catch_and_handle_exception()