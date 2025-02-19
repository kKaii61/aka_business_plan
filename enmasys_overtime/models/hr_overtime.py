import logging
from datetime import datetime
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.addons.resource.models.utils import float_to_time

_logger = logging.getLogger(__name__)


class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = "Overtime"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "x_reference_no"

    x_holiday_status_id = fields.Many2one(
        "hr.leave.type", compute='_compute_from_x_employee_id', store=True, string="Time-Off type", required=True,
        readonly=False, tracking=True,
        domain="""[
            ('company_id', 'in', [x_employee_company_id, False]),
            '|',
                ('requires_allocation', '=', 'no'),
                ('has_valid_allocation', '=', True),
        ]""")
    x_employee_company_id = fields.Many2one(
        comodel_name="res.company", related='x_employee_id.company_id', string="Employee Company", store=True)
    x_employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", tracking=True, required=True, readonly=False,
        compute="_compute_from_x_holiday_type", store=True)
    x_user_id = fields.Many2one(
        comodel_name="res.users", string='User', related='x_employee_id.user_id', related_sudo=True,
        tracking=True, compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    x_description = fields.Char(string="Description", tracking=True, required=True)
    x_interval_duration = fields.Float(
        string="Interval duration", tracking=True, compute="_compute_x_interval_duration", store=True)
    x_holiday_type = fields.Selection(
        selection=[
            ('employee', 'By Employee'), ('company', 'By Company'),
            ('department', 'By Department'), ('category', 'By Employee Tag')
        ], string="Holiday type", tracking=True, default='employee')
    state = fields.Selection(
        selection=[
            ('draft', 'To Submit'), ('confirm', 'To Approve'),
            ('validate1', 'Second Approval'),
            ('bod_approve', "BOD Approved"),
            ('validate', "Validated"),
            ('refuse', 'Refused'),
        ], compute="_compute_state", store=True, tracking=True, copy=False, readonly=False)
    x_manager_id = fields.Many2one(
        comodel_name='hr.employee', compute='_compute_from_x_employee_id', store=True, readonly=False, string="Manager")
    x_mode_company_id = fields.Many2one(
        comodel_name="res.company", compute='_compute_from_x_holiday_type', store=True, string='Mode company',
        tracking=True)
    x_category_id = fields.Many2one(
        comodel_name='hr.employee.category', compute='_compute_from_x_holiday_type', store=True,
        string='Resource Category', help='Category of Employee', tracking=True)
    x_department_id = fields.Many2one(
        'hr.department', compute='_compute_x_department_id', store=True, string='Department', readonly=False,
        tracking=True)
    x_validation_type = fields.Selection(
        string='Validation Type', related='x_holiday_status_id.leave_validation_type', readonly=False)
    x_company_id = fields.Many2one(
        comodel_name="res.company", string="Company", default=lambda self: self.env.company.id)
    x_reference_no = fields.Char(string="Reference No.", default="OT/", tracking=True)
    x_can_approve = fields.Boolean('Can Approve', compute='_compute_x_can_approve')
    x_can_reset = fields.Boolean('Can reset', compute='_compute_x_can_reset')

    @api.depends('x_holiday_status_id')
    def _compute_state(self):
        try:
            for overtime in self:
                overtime.state = 'confirm' if overtime.x_validation_type != 'no_validation' else 'draft'
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_employee_id')
    def _compute_from_x_employee_id(self):
        try:
            for overtime in self:
                overtime.x_manager_id = overtime.x_employee_id.parent_id.id
                if overtime.x_holiday_status_id.requires_allocation == 'no':
                    continue
                if not overtime.x_employee_id:
                    overtime.x_holiday_status_id = False
                elif bool(
                        overtime.x_employee_id.user_id != self.env.user
                        and overtime._origin.x_employee_id != overtime.x_employee_id):
                    if overtime.x_employee_id and not overtime.x_holiday_status_id.with_context(
                            employee_id=overtime.x_employee_id.id).has_valid_allocation:
                        overtime.x_holiday_status_id = False
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_holiday_type')
    def _compute_from_x_holiday_type(self):
        try:
            for overtime in self:
                if overtime.x_holiday_type == 'employee':
                    if not overtime.x_employee_id:
                        overtime.x_employee_id = self.env.user.employee_id
                    overtime.x_mode_company_id = False
                    overtime.x_category_id = False
                elif overtime.x_holiday_type == 'company':
                    overtime.x_employee_id = False
                    if not overtime.x_mode_company_id:
                        overtime.x_mode_company_id = self.env.company.id
                    overtime.x_category_id = False
                elif overtime.x_holiday_type == 'department':
                    overtime.x_employee_id = False
                    overtime.x_mode_company_id = False
                    overtime.x_category_id = False
                elif overtime.x_holiday_type == 'category':
                    overtime.x_employee_id = False
                    overtime.x_mode_company_id = False
                else:
                    overtime.x_employee_id = self.env.context.get('default_employee_id') or self.env.user.employee_id
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_employee_id', 'x_holiday_type')
    def _compute_x_department_id(self):
        try:
            for overtime in self:
                if overtime.x_employee_id:
                    overtime.x_department_id = overtime.x_employee_id.department_id
                elif overtime.x_holiday_type == 'department':
                    if not overtime.x_department_id:
                        overtime.x_department_id = self.env.user.employee_id.department_id
                else:
                    overtime.x_department_id = False
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('state', 'x_employee_id', 'x_department_id')
    def _compute_x_can_approve(self):
        for overtime in self:
            try:
                if overtime.state == 'confirm' and overtime.x_validation_type == 'both':
                    overtime._check_approval_update(state='validate1')
                else:
                    overtime._check_approval_update(state='validate')
            except (AccessError, UserError):
                overtime.x_can_approve = False
            else:
                overtime.x_can_approve = True

    def _check_approval_update(self, state):
        try:
            """ Check if target state is achievable. """
            if self.env.is_superuser():
                return state
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('state', 'x_employee_id', 'x_department_id')
    def _compute_x_can_reset(self):
        for overtime in self:
            try:
                overtime._check_approval_update(state='draft')
            except (AccessError, UserError):
                overtime.x_can_reset = False
            else:
                overtime.x_can_reset = True

    x_working_interval_ids = fields.One2many(
        comodel_name="hr.overtime.interval", string="Working Intervals", inverse_name="x_overtime_id")

    def generate_sequence(self, field):
        try:
            new_sequence = str()
            if field == 'x_reference_no':
                return self._generate_x_ref_no_sequence(leave_type=self.x_holiday_status_id)
            return new_sequence
        except Exception as e:
            raise ValidationError(e)

    def _generate_x_ref_no_sequence(self, leave_type):
        ref_no = "OT/"
        sequence = self.env.ref(
            xml_id='enmasys_overtime.hr_overtime_x_reference_no_sequence', raise_if_not_found=False)
        if not sequence:
            return ref_no
        _leave_type_name = leave_type.name
        _leave_type_code = leave_type.code
        if not _leave_type_code:
            raise UserError(_("Please update %s code before creating new request OT.") % _leave_type_name)
        try:
            _sequence = sequence.sudo()
            overtime_sequence_date_ranges = self.env['ir.sequence.date_range'].sudo().search([
                ('sequence_id', '=', _sequence.id), ('x_leave_type_id', '=', leave_type.id)
            ])
            if not overtime_sequence_date_ranges:
                _its = datetime.now()
                new_date_range = self.env['ir.sequence.date_range'].sudo().create({
                    'sequence_id': _sequence.id,
                    'x_leave_type_id': leave_type.id,
                    'date_from': datetime(year=_its.year, month=1, day=1).date(),
                    'date_to': datetime(year=_its.year, month=12, day=31).date()
                })
                overtime_sequence_date_ranges = new_date_range
            return f"{_leave_type_code}/{overtime_sequence_date_ranges._next()}"
        except Exception as e:
            raise ValidationError(e)

    @api.model_create_multi
    def create(self, vals_list):
        for item in vals_list:
            if not item.get('x_working_interval_ids'):
                raise UserError("Make sure at least Working-Interval")

        new_overtimes = super(HrOvertime, self).create(vals_list)
        for new_overtime in new_overtimes:
            if not self._context.get('leave_fast_create'):
                if new_overtime.x_validation_type == 'no_validation':
                    new_overtime.sudo().action_validate()
            new_overtime.x_reference_no = new_overtime.generate_sequence(field='x_reference_no')
        return new_overtimes

    def get_ot_employees(self, ot_request_type):
        try:
            _default_employees = self.env['hr.employee']
            _ot_employee_domain = {
                'employee': [('id', '=', self.x_employee_id.id)],
                'company': [('company_id', '=', self.x_mode_company_id.id)],
                'department': [('department_id', '=', self.x_department_id.id)],
                'category': [('category_ids', 'in', [self.x_category_id.id])]
            }
            _ot_employees = self.env['hr.employee'].search(
                _ot_employee_domain.get(ot_request_type)
            ) if _ot_employee_domain.get(ot_request_type) else _default_employees
            return _ot_employees
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def action_validate(self):
        try:
            for overtime in self:
                overtime_employees = overtime.get_ot_employees(ot_request_type=overtime.x_holiday_type)
                for working_interval in overtime.x_working_interval_ids:
                    # generate <hr.work.entry> (timesheet)
                    work_entry_values = working_interval.prepare_work_entry_values(employees=overtime_employees)
                    for work_entry_value in work_entry_values:
                        self.env['hr.work.entry'].create(work_entry_value)
                    # generate <resource.calendar.leaves> (timesheet)
                    resource_calendar_leave_vals = working_interval.prepare_resource_calendar_leave_vals(
                        employees=overtime_employees)
                    for resource_calendar_leave_val in resource_calendar_leave_vals:
                        self.env['resource.calendar.leaves'].create(resource_calendar_leave_val)
                overtime.write({'state': 'validate'})
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def action_bod_validate(self):
        try:
            for overtime in self:
                overtime.action_validate()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.depends('x_working_interval_ids.x_approval_hours')
    def _compute_x_interval_duration(self):
        try:
            for overtime in self:
                overtime.x_interval_duration = sum(overtime.x_working_interval_ids.mapped('x_approval_hours'))
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def action_confirm(self):
        try:
            self.write({'state': 'confirm'})
            no_validation_overtimes = self.filtered(lambda ot: ot.x_validation_type == 'no_validation')
            if no_validation_overtimes:
                no_validation_overtimes.sudo().action_validate()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def action_approve(self):
        try:
            CONTEXT = self.env.context
            if CONTEXT.get('reconfirm'):
                action_reconfirm = self.env['ir.actions.actions']._for_xml_id(
                    full_xml_id='enmasys_overtime.reconfirm_overtimes_default_action')
                action_reconfirm['context'] = dict(
                    default_x_overtime_ids=self.ids,
                    default_x_message=_(
                        "Please check the approval hours before approving. If nothing wrong, click 'Confirm' please."))
                return action_reconfirm
            both_approval_overtimes = self.filtered(lambda _overtime: _overtime.x_validation_type == 'both')
            for overtime in both_approval_overtimes:
                overtime.write({'state': 'validate1'})
            hr_and_bod_overtimes = self.filtered(lambda _overtime: _overtime.x_validation_type == 'hr_and_bod')
            for overtime in hr_and_bod_overtimes:
                overtime.write({'state': 'bod_approve'})
            other_overtimes = self.filtered(lambda _overtime: _overtime.x_validation_type not in ['both', 'hr_and_bod'])
            for other_overtime in other_overtimes:
                other_overtime.action_validate()
            return True
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def action_refuse(self):
        try:
            validated_overtimes = self.filtered(lambda otl: otl.state == 'validate1')
            validated_overtimes.write({'state': 'refuse'})
            (self - validated_overtimes).write({'state': 'refuse'})

            for overtime in self:
                overtime.remove_work_entries()
                overtime.remove_resource_leaves()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def remove_work_entries(self):
        return self.env['hr.work.entry'].search([('x_overtime_id', 'in', self.ids)]).unlink()

    def remove_resource_leaves(self):
        return self.env['resource.calendar.leaves'].search([('x_overtime_id', 'in', self.ids)]).unlink()

    def action_draft(self):
        if any(overtime.state not in ['confirm', 'refuse'] for overtime in self):
            raise UserError(
                _('Over time request state must be "Refused" or "To Approve" in order to be reset to draft.'))
        self.state = 'draft'

    @api.constrains('x_working_interval_ids')
    def _constrains_all_working_intervals_must_same_month(self):
        working_interval_months = [
            working_interval.x_working_date.month for working_interval in self.x_working_interval_ids.sudo()]
        unique_working_interval_months = list(set(sorted(working_interval_months)))
        self._from_unique_months_raise_working_interval_months_warning(unique_months=unique_working_interval_months)

    @staticmethod
    def _from_unique_months_raise_working_interval_months_warning(unique_months, raise_warning=True):
        _valid_unique_months = True if len(unique_months) == 1 else False
        if _valid_unique_months:
            return
        if not raise_warning:
            return _valid_unique_months
        _what_warning = _("Cant create or edit the Over-Time request that not same month")
        _current_over_time_months = _("Current months")
        _over_time_months = ', '.join([str(month) for month in sorted(unique_months)])
        _solution = _("Please create another requests, or adjust dates. Thanks")
        _warning = f"{_what_warning} ({_current_over_time_months}: {_over_time_months}). {_solution}."
        raise UserError(_warning)

    x_overtime_working_type_ids = fields.Many2many(
        comodel_name="hr.work.entry.type", string="Overtime Working-Types",
        relation="hr_overtime_work_entry_type_rel", column1="overtime_id", column2="type_id",
        related="x_holiday_status_id.x_overtime_working_type_ids")
    x_overtime_start_at = fields.Datetime(
        string="Worked start at", compute='_compute_working_times', store=True, tracking=True)
    x_overtime_end_at = fields.Datetime(
        string="Worked end at", compute='_compute_working_times', store=True, tracking=True)

    def _to_utc(self, date, hour, resource):
        """
        clone function '_to_utc' of core model <hr.leave>
        """
        hour = float_to_time(float(hour))
        holiday_tz = timezone(resource.tz or self.env.user.tz or 'UTC')
        return holiday_tz.localize(datetime.combine(date, hour)).astimezone(UTC).replace(tzinfo=None)

    @api.depends(
        'x_working_interval_ids.x_working_date',
        'x_working_interval_ids.x_actual_start_date', 'x_working_interval_ids.x_actual_end_date')
    def _compute_working_times(self):
        try:
            for overtime in self.filtered(lambda ho: ho.x_working_interval_ids):
                working_times_collection = {
                    working_interval.x_working_date: {
                        'time_start': working_interval.x_actual_start_date,
                        'time_end': working_interval.x_actual_end_date
                    }
                    for working_interval in overtime.x_working_interval_ids
                }
                _min_working_date = min(working_times_collection.keys())
                _max_working_date = max(working_times_collection.keys())
                overtime.x_overtime_start_at = self._to_utc(
                    date=_min_working_date,
                    hour=float(working_times_collection.get(_min_working_date).get('time_start')),
                    resource=overtime.x_employee_id
                )
                overtime.x_overtime_end_at = self._to_utc(
                    date=_max_working_date,
                    hour=float(working_times_collection.get(_max_working_date).get('time_end')),
                    resource=overtime.x_employee_id
                )
            for overtime in self.filtered(lambda ho: not ho.x_working_interval_ids):
                overtime.x_overtime_start_at = overtime.x_overtime_end_at = False
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)
