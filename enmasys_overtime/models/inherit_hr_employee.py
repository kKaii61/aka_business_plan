import logging
import pytz
from collections import defaultdict
from datetime import datetime, time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InheritHrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_consumed_leaves(self, leave_types, target_date=False, ignore_future=False):
        try:
            consumed_leaves = super(InheritHrEmployee, self)._get_consumed_leaves(
                leave_types=leave_types, target_date=target_date, ignore_future=ignore_future)
            if self.env.context.get('overtime_employee'):
                return self._get_consumed_overtime(
                    leave_types=leave_types, target_date=target_date, ignore_future=ignore_future)
            return consumed_leaves
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def _get_consumed_overtime(self, leave_types, target_date=False, ignore_future=False):
        try:
            """
            Cover function _get_consumed_leaves() in core hr_holidays for model hr.overtime
            """
            employees = self or self._get_contextual_employee()
            overtimes_domain = [
                ('x_holiday_status_id', 'in', leave_types.ids),
                ('x_employee_id', 'in', employees.ids),
                ('state', 'in', ['confirm', 'validate1', 'validate', 'bod_approve']),
            ]
            if self.env.context.get('ignored_leave_ids'):
                overtimes_domain.append(('id', 'not in', self.env.context.get('ignored_leave_ids')))

            if not target_date:
                target_date = fields.Date.today()
            if ignore_future or not ignore_future:
                pass
            overtimes = self.env['hr.overtime'].search(overtimes_domain)
            overtimes_per_employee_type = defaultdict(lambda: defaultdict(lambda: self.env['hr.overtime']))
            for overtime in overtimes:
                overtimes_per_employee_type[overtime.x_employee_id][overtime.x_holiday_status_id] |= overtime

            allocations = self.env['hr.leave.allocation'].with_context(active_test=False).search([
                ('employee_id', 'in', employees.ids),
                ('holiday_status_id', 'in', leave_types.ids),
                ('state', '=', 'validate'),
            ]).filtered(lambda al: al.active or not al.employee_id.active)
            allocations_per_employee_type = defaultdict(lambda: defaultdict(lambda: self.env['hr.leave.allocation']))
            for allocation in allocations:
                allocations_per_employee_type[allocation.employee_id][allocation.holiday_status_id] |= allocation

            allocations_leaves_consumed = defaultdict(
                lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))

            to_recheck_leaves_per_leave_type = defaultdict(lambda:
                                                           defaultdict(lambda: {
                                                               'excess_days': defaultdict(lambda: {
                                                                   'amount': 0,
                                                                   'is_virtual': True,
                                                               }),
                                                               'exceeding_duration': 0,
                                                               'to_recheck_leaves': self.env['hr.leave']
                                                           })
                                                           )
            for allocation in allocations:
                allocation_data = allocations_leaves_consumed[allocation.employee_id][allocation.holiday_status_id][
                    allocation]
                future_leaves = 0
                if allocation.allocation_type == 'accrual':
                    future_leaves = allocation._get_future_leaves_on(target_date)
                max_leaves = allocation.number_of_hours_display \
                    if allocation.type_request_unit in ['hour'] \
                    else allocation.number_of_days_display
                max_leaves += future_leaves
                allocation_data.update({
                    'max_leaves': max_leaves,
                    'accrual_bonus': future_leaves,
                    'virtual_remaining_leaves': max_leaves,
                    'remaining_leaves': max_leaves,
                    'leaves_taken': 0,
                    'virtual_leaves_taken': 0,
                })

            for employee in employees:
                for leave_type in leave_types:
                    allocations_with_date_to = self.env['hr.leave.allocation']
                    allocations_without_date_to = self.env['hr.leave.allocation']
                    for leave_allocation in allocations_per_employee_type[employee][leave_type]:
                        if leave_allocation.date_to:
                            allocations_with_date_to |= leave_allocation
                        else:
                            allocations_without_date_to |= leave_allocation
                    sorted_leave_allocations = allocations_with_date_to.sorted(
                        key='date_to') + allocations_without_date_to

                    leave_duration_field = 'x_interval_duration'
                    if leave_type.request_unit in ['day', 'half_day']:
                        leave_unit = 'days'
                    else:
                        leave_unit = 'hours'

                    overtime_type_data = allocations_leaves_consumed[employee][leave_type]
                    for overtime in overtimes_per_employee_type[employee][leave_type]:
                        leave_duration = overtime[leave_duration_field]
                        skip_excess = False

                        if sorted_leave_allocations.filtered(
                                lambda alloc: alloc.allocation_type == 'accrual'):
                            to_recheck_leaves_per_leave_type[employee][leave_type]['to_recheck_leaves'] |= overtime
                            skip_excess = True
                            continue

                        if leave_type.requires_allocation == 'yes':
                            for allocation in sorted_leave_allocations:
                                interval_start = datetime.combine(allocation.date_from, time.min)
                                interval_end = datetime.combine(
                                    allocation.date_to or datetime.now().date(), time.max)

                                duration_info = employee._get_calendar_attendances(
                                    interval_start.replace(tzinfo=pytz.UTC), interval_end.replace(tzinfo=pytz.UTC))
                                duration = duration_info['hours' if leave_unit == 'hours' else 'days']
                                max_allowed_duration = min(
                                    duration,
                                    overtime_type_data[allocation]['virtual_remaining_leaves']
                                )

                                if not max_allowed_duration:
                                    continue

                                allocated_time = min(max_allowed_duration, leave_duration)
                                overtime_type_data[allocation]['virtual_leaves_taken'] += allocated_time
                                overtime_type_data[allocation]['virtual_remaining_leaves'] -= allocated_time
                                if overtime.state == 'validate':
                                    overtime_type_data[allocation]['leaves_taken'] += allocated_time
                                    overtime_type_data[allocation]['remaining_leaves'] -= allocated_time

                                leave_duration -= allocated_time
                                if not leave_duration:
                                    break
                            if round(leave_duration, 2) > 0 and not skip_excess:
                                to_recheck_leaves_per_leave_type[employee][leave_type]['excess_days'][
                                    overtime.x_overtime_end_at.date()] = {
                                    'amount': leave_duration,
                                    'is_virtual': overtime.state != 'validate',
                                    'x_overtime_id': overtime.id,
                                }
                        else:
                            allocated_time = overtime.x_interval_duration
                            overtime_type_data[False]['virtual_leaves_taken'] += allocated_time
                            overtime_type_data[False]['virtual_remaining_leaves'] = 0
                            overtime_type_data[False]['remaining_leaves'] = 0
                            if overtime.state == 'validate':
                                overtime_type_data[False]['leaves_taken'] += allocated_time

            for employee in to_recheck_leaves_per_leave_type:
                for leave_type in to_recheck_leaves_per_leave_type[employee]:
                    content = to_recheck_leaves_per_leave_type[employee][leave_type]
                    consumed_content = allocations_leaves_consumed[employee][leave_type]
                    if content['to_recheck_leaves']:
                        date_to_simulate = max(content['to_recheck_leaves'].mapped('date_from')).date()
                        latest_accrual_bonus = 0
                        date_accrual_bonus = 0
                        virtual_remaining = 0
                        additional_leaves_duration = 0
                        for allocation in consumed_content:
                            latest_accrual_bonus += allocation and allocation._get_future_leaves_on(date_to_simulate)
                            date_accrual_bonus += consumed_content[allocation]['accrual_bonus']
                            virtual_remaining += consumed_content[allocation]['virtual_remaining_leaves']
                        for leave in content['to_recheck_leaves']:
                            additional_leaves_duration += leave.number_of_hours if leave_type.request_unit == 'hours' else leave.number_of_days
                        latest_remaining = virtual_remaining - date_accrual_bonus + latest_accrual_bonus
                        content['exceeding_duration'] = round(min(0, latest_remaining - additional_leaves_duration), 2)

            return (allocations_leaves_consumed, to_recheck_leaves_per_leave_type)
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)
