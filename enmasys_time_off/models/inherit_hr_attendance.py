from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InheritHrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.model
    def create(self, vals):
        try:
            new_attendance = super().create(vals)

            checkin_date = new_attendance.check_in.strftime('%Y-%m-%d')
            working_shift_registered_in_checkin_date = new_attendance.env['working.shift.register'].search([
                ('x_registered_date', '=', checkin_date)
            ], order="x_working_shift_to DESC", limit=1)
            if working_shift_registered_in_checkin_date:
                working_shift_registered_in_checkin_date.sudo().write({
                    'x_check_in_time': new_attendance.check_in,
                    'x_check_out_time': new_attendance.check_out,
                })
            return new_attendance
        except Exception as e:
            raise ValidationError(e)

    def write(self, changes):
        try:
            check_out_time = False
            if 'check_out' in changes.keys():
                check_out_time = changes.get('check_out')

            res = super().write(changes)

            checkin_date = self.check_in.strftime('%Y-%m-%d')
            working_shift_registered_in_checkin_date = self.env['working.shift.register'].search([
                ('x_registered_date', '=', checkin_date)
            ], order="x_working_shift_to DESC", limit=1)
            if working_shift_registered_in_checkin_date:
                working_shift_registered_in_checkin_date.sudo().write({
                    'x_check_out_time': check_out_time
                })

            return res
        except Exception as e:
            raise ValidationError(e)