from odoo import _, api, fields, models
from odoo.exceptions import UserError
import pytz
from pytz import UTC


class InheritHrAttendance(models.Model):
    _inherit = 'hr.attendance'

    x_state = fields.Selection(selection=[('waiting_confirmation', 'Chờ cấp trên xác nhận'), 
                                        ('confirmed', 'Đã xác nhận')],
                                        string='State', default='waiting_confirmation', tracking=True)

    @api.model
    def create(self, vals):
        res = super(InheritHrAttendance, self).create(vals)
        if res.check_out:
            worktime, lunchtime = res.get_time_resource_calendar()
            if (res.worked_hours - lunchtime - worktime < 0):
                res.x_state = 'waiting_confirmation'
            else:
                res.x_state = 'confirmed'
        return res

    def write(self, vals):
        res = super(InheritHrAttendance, self).write(vals)
        # set state is waiting confirmation when checkin outside company, checkin outside working hour, checkout by the system and not working enough hours
        if vals.get('check_out'):
            worktime, lunchtime = self.get_time_resource_calendar()
            if (self.worked_hours - lunchtime - worktime < 0) and (not vals.get('x_state') and self.x_state != 'confirmed'):
                self.x_state = 'waiting_confirmation'
            else:
                self.x_state = 'confirmed'
        # create work entry when confirmed attendance
        if vals.get('x_state') == 'confirmed':
            if self.check_out:
                date_checkin = fields.Datetime.to_datetime(self.check_in).replace(tzinfo=UTC).astimezone(
                    pytz.timezone(self.env.user.tz))
                if 0 <= date_checkin.hour < 12:
                    date_start = date_checkin.replace(hour=5).astimezone(pytz.utc)
                elif 12 <= date_checkin.hour < 24:
                    date_start = date_checkin.replace(hour=12).astimezone(pytz.utc)
                date_checkout = fields.Datetime.to_datetime(self.check_out).replace(tzinfo=UTC).astimezone(
                    pytz.timezone(self.env.user.tz))
                if 0 <= date_checkout.hour <= 12:
                    date_stop = date_checkout.replace(hour=12).astimezone(pytz.utc)
                elif 12 < date_checkout.hour < 24:
                    date_stop = date_checkout.replace(hour=22).astimezone(pytz.utc)
                work_entries_values = self.employee_id.contract_id._get_work_entries_values(date_start, date_stop)
                if work_entries_values:
                    self.env['hr.work.entry'].sudo().create(work_entries_values)
            else:
                raise UserError('Phiếu chấm công của nhân viên [%s] %s vào lúc %s chưa thực hiện đăng xuất.'
                                % (self[0].employee_id.x_code_employee, self[0].employee_id.name,
                                   self[0].check_in.strftime('%H:%M:%S %d/%m/%Y')))
        return res

    def get_time_resource_calendar(self):
        resource_calendar = self.employee_id.contract_id.resource_calendar_id
        date_checkout = fields.Datetime.to_datetime(self.check_out).replace(tzinfo=UTC).astimezone(
            pytz.timezone(self.env.user.tz))
        lunchtime = 0
        worktime = 0
        start_time = 0
        end_time = 0
        if resource_calendar:
            attendances = resource_calendar.attendance_ids.filtered(
                lambda rc: rc.dayofweek == str(self.check_out.weekday()))
            for attendance in attendances:
                date_start = date_checkout.replace(hour=int(attendance.hour_from),
                                                    minute=int(attendance.hour_from % 1 * 60), second=0).astimezone(
                    pytz.utc)
                date_stop = date_checkout.replace(hour=int(attendance.hour_to),
                                                    minute=int(attendance.hour_to % 1 * 60), second=0).astimezone(
                    pytz.utc)
                work_entry_holiday = self.env['hr.work.entry'].sudo().search(
                    [('employee_id', '=', self.employee_id.id), ('work_entry_type_id.is_leave', '=', True),
                        ('date_start', '<=', date_start), ('date_stop', '>=', date_stop)])
                if not work_entry_holiday:
                    worktime += (attendance.hour_to - attendance.hour_from)
                    if attendance.day_period == 'morning' or not start_time:
                        start_time = attendance.hour_from
                    if attendance.day_period == 'afternoon' or not end_time:
                        end_time = attendance.hour_to
        if start_time > 0 and end_time > 0:
            lunchtime = end_time - start_time - worktime
        return worktime, lunchtime
    
    def action_confirm(self):
        for record in self:
            record.sudo().write({'x_state': 'confirmed'})