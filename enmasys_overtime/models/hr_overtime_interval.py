import logging
from datetime import datetime, timedelta
from dateutil import tz
from pytz import UTC

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

from .inherit_res_company import OVERTIME_INTERVALS
from ..overtime_overtime import OvertimeOvertime

_logger = logging.getLogger(__name__)


class HrOvertimeInterval(models.Model):
    _name = "hr.overtime.interval"
    _description = "Overtime: Interval"
    _order = "x_working_date"
    # inverse_name
    x_overtime_id = fields.Many2one(comodel_name="hr.overtime", string="Overtime", ondelete="cascade")

    # interval-in4
    x_working_type_id = fields.Many2one(comodel_name="hr.work.entry.type", string="Working type", required=True)
    x_description = fields.Char(string="Description")
    x_working_date = fields.Date(string="Working date", required=True)
    x_estimated_start_date = fields.Selection(
        selection=OVERTIME_INTERVALS, string="Estimated interval from", required=True)
    x_estimated_end_date = fields.Selection(selection=OVERTIME_INTERVALS, string="Estimated interval to", required=True)
    x_estimated_hours = fields.Float(
        string="Estimated Hours", compute='_compute_x_estimated_hours', readonly=False, store=True)
    x_actual_start_date = fields.Selection(selection=OVERTIME_INTERVALS, string="Actual start time")
    x_actual_end_date = fields.Selection(selection=OVERTIME_INTERVALS, string="Actual end time")
    x_hours_actual = fields.Float(
        string="Working hours actually", compute='_compute_x_hours_actual', readonly=False, store=True)
    x_approval_hours = fields.Float(
        string="Approved hours", compute="_compute_x_approval_hours", store=True, readonly=False)
    x_employee_id = fields.Many2one(comodel_name="hr.employee", related='x_overtime_id.x_employee_id', store=True)

    @api.model
    def default_get(self, fields):
        try:
            defaults = super(HrOvertimeInterval, self).default_get(fields)
            _default_start_time = self.env.company.x_default_estimated_ot_start_time
            _default_end_time = self.env.company.x_default_estimated_ot_end_time
            defaults['x_estimated_start_date'] = defaults['x_actual_start_date'] = _default_start_time
            defaults['x_estimated_end_date'] = defaults['x_actual_end_date'] = _default_end_time
            return defaults
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def _get_overtime_intervals(self, ot_from, ot_to):
        _company = self.env.company
        _lunch_from = _company.x_over_time_lunch_from
        _lunch_to = _company.x_over_time_lunch_to
        _lunch_intervals = _lunch_to - _lunch_from
        _overtime_intervals = float(ot_to) - float(ot_from)
        if bool(float(ot_from) <= _lunch_from and _lunch_to <= float(ot_to)):
            return _overtime_intervals - _lunch_intervals
        return _overtime_intervals

    @api.depends('x_estimated_start_date', 'x_estimated_end_date')
    def _compute_x_estimated_hours(self):
        try:
            for interval in self:
                interval.x_estimated_hours = self._get_overtime_intervals(
                    ot_from=interval.x_estimated_start_date, ot_to=interval.x_estimated_end_date)
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_actual_start_date', 'x_actual_end_date')
    def _compute_x_hours_actual(self):
        try:
            for interval in self:
                interval.x_hours_actual = self._get_overtime_intervals(
                    ot_from=interval.x_actual_start_date, ot_to=interval.x_actual_end_date)
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.onchange('x_estimated_start_date', 'x_estimated_end_date')
    def _onchange_estimated(self):
        try:
            for interval in self:
                if interval.x_estimated_start_date and interval.x_estimated_end_date:
                    interval.x_actual_start_date = interval.x_estimated_start_date
                    interval.x_actual_end_date = interval.x_estimated_end_date
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_hours_actual')
    def _compute_x_approval_hours(self):
        try:
            for line in self:
                line.x_approval_hours = line.x_hours_actual
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.onchange('x_estimated_start_date', 'x_estimated_end_date')
    def onchange_estimated_date(self):
        for overtime in self:
            if overtime.x_estimated_start_date and overtime.x_estimated_end_date:
                if overtime.x_estimated_hours <= 0:
                    raise UserError(_("Estimated start can be after Estimated to. Please check again."))

    @api.onchange('x_actual_start_date', 'x_actual_end_date')
    def onchange_actual_date(self):
        for overtime in self:
            if overtime.x_actual_start_date and overtime.x_actual_end_date:
                if overtime.x_hours_actual <= 0:
                    raise UserError(_("Actual start cant be after Actual end. Please check again."))

    @classmethod
    def _get_interval_fields(cls, interval_type='estimated'):
        try:
            if interval_type == 'estimated':
                return 'x_estimated_start_date', 'x_estimated_end_date'
            elif interval_type == 'actual':
                return 'x_actual_start_date', 'x_actual_end_date'
            else:
                # In future, If necessary to get another interval fields, inherit this or modify this and return
                # interval-start,end-fields
                return str(), str()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def get_overlapped_intervals(self, employee_id, working_date, ot_from, ot_to, interval_type='estimated'):
        try:
            _over_time = OvertimeOvertime(
                over_time_date=working_date, overtime_start=float(ot_from), overtime_end=float(ot_to))
            _start_field, _end_field = self._get_interval_fields(interval_type=interval_type)
            if not _start_field or not _end_field:
                return self.env['hr.overtime.interval']
            return self.env['hr.overtime.interval'].search([
                ('x_employee_id', '=', employee_id), ('x_working_date', '=', working_date),
            ]).filtered(lambda oti: oti != self and _over_time.check_overlapped(
                range_start=float(oti[_start_field]), range_to=float(oti[_end_field])))
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.constrains(
        'x_estimated_start_date', 'x_estimated_end_date', 'x_actual_start_date', 'x_actual_end_date',
        'x_employee_id', 'x_working_date')
    def _constrain_not_overlapped_date_ranges(self):
        try:
            _user_error = UserError(_("Cant create OverTime that is overlapped with other one. Please check again"))
            for line in self:
                _overlapped_records = self.env['hr.overtime.interval']
                if line.x_estimated_end_date and line.x_estimated_start_date:
                    _overlapped_records = line.get_overlapped_intervals(
                        employee_id=line.x_employee_id.id, working_date=line.x_working_date,
                        ot_from=line.x_estimated_start_date, ot_to=line.x_estimated_end_date)
                if line.x_actual_start_date and line.x_actual_end_date:
                    _overlapped_records = line.get_overlapped_intervals(
                        employee_id=line.x_employee_id.id, working_date=line.x_working_date,
                        ot_from=line.x_actual_start_date, ot_to=line.x_actual_end_date,
                        interval_type='actual')
                if _overlapped_records:
                    raise _user_error
        except Exception as e:
            _logger.exception(msg=e)
            raise UserError(e)

    def prepare_resource_calendar_leave_vals(self, employees):
        try:
            resource_calendar_leave_vals = list()
            for employee in employees:
                resource_calendar_leave_val = dict()
                employee_contract = employee._get_contracts(
                    date_from=self.x_working_date, date_to=self.x_working_date)
                if not employee_contract:
                    continue
                date = datetime.strptime(datetime.combine(self.x_working_date, datetime.strptime(
                    dict(self._fields['x_actual_start_date'].selection).get(self.x_actual_start_date),
                    '%I:%M %p').time()).replace(tzinfo=tz.gettz(self.env.user.tz)).astimezone(UTC).strftime(
                    "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                resource_calendar_leave_val['name'] = self.x_description or str()
                resource_calendar_leave_val['work_entry_type_id'] = self.x_working_type_id.id
                resource_calendar_leave_val['date_from'] = date
                resource_calendar_leave_val['date_to'] = date + timedelta(hours=self.x_approval_hours)
                resource_calendar_leave_val['resource_id'] = employee.resource_id.id
                resource_calendar_leave_val['x_overtime_id'] = self.x_overtime_id.id
                resource_calendar_leave_val['time_type'] = self.x_overtime_id.x_holiday_status_id.time_type
                resource_calendar_leave_vals.append(resource_calendar_leave_val)
            return resource_calendar_leave_vals
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def prepare_work_entry_values(self, employees):
        work_entry_name = _("%s : %s") % (self.x_working_type_id.name, self.x_employee_id.name)
        date_start = datetime.strptime(datetime.combine(self.x_working_date, datetime.strptime(
            dict(self._fields['x_actual_start_date'].selection).get(self.x_actual_start_date),
            '%I:%M %p').time()).replace(tzinfo=tz.gettz(self.env.user.tz)).astimezone(UTC).strftime(
            "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        work_entry_values = list()
        for employee in employees:
            if not employee._get_contracts(date_from=self.x_working_date, date_to=self.x_working_date):
                continue
            work_entry_val = {
                'name': work_entry_name,
                'employee_id': employee.sudo().id,
                'work_entry_type_id': self.x_working_type_id.id,
                'duration': self.x_hours_actual,
                'state': 'draft',
                'date_start': date_start,
                'date_stop': date_start + timedelta(hours=self.x_approval_hours),
                'x_overtime_id': self.x_overtime_id.id
            }
            work_entry_values.append(work_entry_val)
        return work_entry_values

