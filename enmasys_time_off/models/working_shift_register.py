from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime

from odoo.exceptions import ValidationError as popUpNotify
from datetime import datetime, timedelta
from pytz import UTC
from dateutil import tz

class WorkingShiftRegister(models.Model):
    _name = "working.shift.register"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Working shift register"
    _rec_name = "x_registered_employee_id"

    # new
    x_registered_employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Registered Employee", tracking=True, required=True)
    x_registered_employee_department_id = fields.Many2one(
        comodel_name="hr.department", string="Registered Employee's department", tracking=True,
        related="x_registered_employee_id.department_id", store=True
    )
    x_registered_date = fields.Date(string="Registered date", tracking=True, required=True, default=fields.Date.today)
    x_day_of_week = fields.Char(
        string="Day of week", tracking=True, readonly=True, store=True,
        )
    x_working_shift_id = fields.Many2one(
        comodel_name="working.shift", string="Working shift", tracking=True, required=True, )
    x_working_shift_from = fields.Float(
        string="Working shift from", tracking=True, store=True, related="x_working_shift_id.x_shift_from")
    x_working_shift_to = fields.Float(
        string="Working shift to", tracking=True, store=True, related="x_working_shift_id.x_shift_to")
    x_working_type = fields.Selection(
        selection=[('complete_attendance', "Attendance completely"),
                   ('late_in_early_out', "Late Checkin/Early Check-Out"),
                   ('not_checkin', "Not checkin"),
                   ('unexcused_absence', "Unexcused Absence")], tracking=True, string="Working type",
        compute="_compute_x_working_type", store=True,
    )
    x_check_in_time = fields.Datetime(string="Check In time", tracking=True, readonly=True)
    x_check_in_type = fields.Selection(
        selection=[('late_in_early_out', "Late Checkin/Early Check-Out"),
                   ('checkin_late_with_permission', "Checkin late with permission"),
                   ('checkin_late_without_permission', "Checkin late without permission")], tracking=True,
        string="Checkin type", compute="_compute_x_check_in_type", store=True,
    )
    x_check_out_time = fields.Datetime(string="Check Out time", tracking=True, readonly=True)
    x_check_out_type = fields.Selection(
        selection=[('late_in_early_out', "Late Checkin/Early Check-Out"),
                   ('checkin_late_with_permission', "With permission"),
                   ('checkin_late_without_permission', "Without permission")], tracking=True,
        string="Checkout type", compute="_compute_x_check_out_type", store=True)
    state = fields.Selection(
        selection=[('request', "Yêu cầu"),
                   ('confirm', "Xác nhận"),
                   ('timekeeping', "Đã chấm công"),
                   ('cancel', "Hủy")], tracking=True, string="Status", default='request')

    # x_day_of_week = fields.Char(string="Day of week", tracking=True, readonly=True, store=True,
    #                             )
    date_start = fields.Datetime(string='Ngày bắt đầu', compute='_compute_date_start_end', store=True)
    date_stop = fields.Datetime(string='Ngày kết thúc', compute='_compute_date_start_end', store=True)
    color = fields.Integer(string='Color', compute='_compute_color', store=True)

    @api.depends('x_check_out_time', 'x_working_shift_to', 'state')
    def _compute_x_check_out_type(self):
        try:
            for registration in self:
                checkout = registration.x_check_out_time
                shift_to_time = registration.x_working_shift_to
                if not checkout or not shift_to_time:
                    registration.x_check_out_type = ''
                    continue
                checkout_with_format_time = datetime.strptime(str(checkout), '%Y-%m-%d %H:%M:%S').time()
                checkout_time = checkout_with_format_time.hour + 7 + (checkout_with_format_time.hour / 60) + (
                        checkout_with_format_time.second / 360)
                if checkout_time < shift_to_time:
                    registration.x_check_out_type = 'late_in_early_out'
                    continue
        except Exception as e:
            raise ValidationError(e)

    @api.depends('x_check_in_time', 'x_working_shift_from', 'state')
    def _compute_x_check_in_type(self):
        try:
            for registration in self:
                checkin = registration.x_check_in_time
                shift_from_time = registration.x_working_shift_from
                if not checkin or not shift_from_time:
                    registration.x_check_in_type = ''
                    continue
                checkin_with_format_time = datetime.strptime(str(checkin), '%Y-%m-%d %H:%M:%S').time()
                checkin_time = checkin_with_format_time.hour + 7 + (checkin_with_format_time.hour / 60) + (
                        checkin_with_format_time.second / 360)
                if checkin_time > shift_from_time:
                    registration.x_check_in_type = 'late_in_early_out'
                    continue
        except Exception as e:
            raise ValidationError(e)

    @api.depends('x_check_in_time', 'x_check_out_time', 'x_working_shift_from', 'x_working_shift_to',
                 'state')
    def _compute_x_working_type(self):
        try:
            for registration in self:
                checkin = registration.x_check_in_time
                checkout = registration.x_check_out_time
                shift_from = registration.x_working_shift_from
                shift_to = registration.x_working_shift_to

                if registration.state in ['confirm', 'timekeeping', 'cancel']:
                    if not checkin or not checkout:
                        registration.x_working_type = 'not_checkin'
                        continue

                    checkin_with_format_time = datetime.strptime(str(checkin), '%Y-%m-%d %H:%M:%S').time()
                    checkin_time = checkin_with_format_time.hour + 7 + (checkin_with_format_time.hour / 60) + (
                            checkin_with_format_time.second / 360)

                    checkout_with_format_time = datetime.strptime(str(checkout), '%Y-%m-%d %H:%M:%S').time()
                    checkout_time = checkout_with_format_time.hour + 7 + (checkout_with_format_time.hour / 60) + (
                            checkout_with_format_time.second / 360)

                    if shift_from and shift_to:
                        if checkin_time <= shift_from and checkout_time >= shift_to:
                            registration.x_working_type = 'complete_attendance'
                            continue
                        if checkin_time > shift_to or checkout_time < shift_from:
                            registration.x_working_type = 'late_in_early_out'
                            continue
                else:
                    registration.x_working_type = False
        except Exception as e:
            raise ValidationError(e)

    # @api.depends('x_registered_date')
    # def _convert_x_registered_date_into_x_day_of_week(self):
    #     try:
    #         for registration in self:
    #             day_of_week = registration.x_registered_date.strftime('%A')
    #             registration.x_day_of_week = registration.env['ir.translation'].search([
    #                 ('src', '=', day_of_week), ('module', '=', 'base')
    #             ], limit=1).value
    #     except Exception as e:
    #         raise popUpNotify(e)
    
    @api.depends('x_working_shift_id', 'x_registered_date')
    def _compute_date_start_end(self):

        def twelve_hour_format(time:float):
            hours = int(time)
            minutes = int((time - hours) * 60)
            meridian = 'AM'
            if hours >= 12:
                meridian = 'PM'
                if hours > 12:
                    hours -= 12
            if hours == 0:
                hours = 12
            return f"{hours}:{minutes:02d} {meridian}"

        def combine_convert_tz(date, time:str):
            return datetime.strptime(datetime.combine(date, datetime.strptime(time,
            '%I:%M %p').time()).replace(tzinfo=tz.gettz(self.env.user.tz)).astimezone(UTC).strftime(
            "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

        for record in self:
            if record.x_working_shift_id and record.x_registered_date:
                record.date_start = combine_convert_tz(record.x_registered_date, twelve_hour_format(record.x_working_shift_id.x_shift_from))
                record.date_stop = combine_convert_tz(record.x_registered_date, twelve_hour_format(record.x_working_shift_id.x_shift_to))
            else:
                record.date_start = None
                record.date_stop = None
    
    @api.depends('state')
    def _compute_color(self):
        for record in self:
            if record.state == 'request':
                record.color = 3
            elif record.state == 'confirm':
                record.color = 10
            elif record.state == 'timekeeping':
                record.color = 7
            else:
                record.color = 1

    def nude_this_registration(self):
        try:
            self.ensure_one()
            this = self

            action_return = {
                'type': 'ir.actions.act_window',
                'res_id': this.id,
                'res_model': this._name,
                'view_mode': 'form',
                'context': {
                    'create': True
                }
            }

            return action_return
        except Exception as e:
            raise ValidationError(e)

    def cancel_this_registration(self):
        try:
            for registration in self:
                registration.write({
                    'state': 'cancel'
                })
        except Exception as e:
            raise ValidationError(e)

    def make_this_registration_had_timekeeping(self):
        try:
            for registration in self:
                registration.write({
                    'state': 'timekeeping'
                })
        except Exception as e:
            raise ValidationError(e)

    def confirm_this_registration(self):
        try:
            for registration in self:
                registration.write({
                    'state': 'confirm'
                })
        except Exception as e:
            raise ValidationError(e)

    def name_get(self):
        def hour_format(time:float):
            hours = int(time)
            minutes = int((time - hours) * 60)
            if hours == 0:
                hours = 12
            if minutes != 0:
                return f"{hours}:{minutes:02d}h"
            else:
                return f"{hours}h"

        try:
            display_names = super().name_get()

            for registration in self:
                display_name = f"{hour_format(registration.x_working_shift_id.x_shift_from)} - {hour_format(registration.x_working_shift_id.x_shift_to)}: {registration.x_working_shift_id.x_shift_name }"
                display_names.append((registration.id, display_name))

            return display_names
        except Exception as e:
            raise ValidationError(e)
    
    def copy_last_week(self, date_start, date_stop):
        date_start = fields.Date.to_date(date_start)    
        date_stop = fields.Date.to_date(date_stop)
        if (date_stop - date_start).days == 6:
            workings = self.env['working.shift.register'].search([('x_registered_date', '>=', date_start), ('x_registered_date', '<=', date_stop)])
            if workings:
                raise UserError(_('Tuần này đã có đăng ký ca. Không thể sao chép'))
            else:
                workings_last_week = self.env['working.shift.register'].search([('x_registered_date', '>=', date_start - timedelta(days=7)), ('x_registered_date', '<=', date_stop - timedelta(days=7)), ('state', 'in', ['confirm', 'timekeeping'])])
                for woking in workings_last_week:
                    self.env['working.shift.register'].create({
                        'x_registered_employee_id': woking.x_registered_employee_id.id,
                        'x_registered_date': woking.x_registered_date + timedelta(days=7),
                        'x_working_shift_id': woking.x_working_shift_id.id,
                    })
                return True
        return False