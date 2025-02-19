import logging
from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, get_lang

_logger = logging.getLogger(__name__)


class OverTimeReportSummaryLine(models.TransientModel):
    _name = "over.time.report.summary.line"
    _description = "Report: OVER-TIME line (summarized)"

    # inverse_name
    x_over_time_report_id = fields.Many2one(
        comodel_name="over.time.report", string="REPORT: OVER-TIME", ondelete="cascade")

    # each-line
    x_employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    x_employee_position_id = fields.Many2one(
        comodel_name="hr.job", string="Employee's position", related="x_employee_id.job_id")
    x_employee_department_id = fields.Many2one(
        comodel_name="hr.department", string="Employee's department", related="x_employee_id.department_id")
    x_total_allocated_hours = fields.Float(
        string="Total allocated hours", default=0, compute="_compute_hours", store=True)
    x_total_validated_hours = fields.Float(
        string="Total validated hours", default=0, compute="_compute_hours", store=True)
    x_total_remaining_hours = fields.Float(
        string="Total remaining hours", default=0, compute="_compute_hours", store=True)
    x_over_time_report_detail_line_ids = fields.Many2many(
        comodel_name="over.time.report.detail.line", string="Detail lines",
        relation="summary_detail_rel", column1="summary_id", column2="detail_id")

    @api.depends('x_over_time_report_detail_line_ids')
    def _compute_hours(self):
        try:
            for line in self:
                line.x_total_allocated_hours = 0
                line.x_total_validated_hours = 0
                line.x_total_remaining_hours = 0
                if not line.x_over_time_report_detail_line_ids:
                    continue
                detail_lines = line.x_over_time_report_detail_line_ids.filtered(
                    lambda dl: dl.x_overtime_id.state == 'validate' and dl.x_employee_id == line.x_employee_id)
                total_validated_hours = sum([detail_line.x_over_time_duration for detail_line in detail_lines] or [])
                origin_over_time_records = line.x_over_time_report_detail_line_ids.x_overtime_id
                allocations = self.env['hr.leave.allocation'].sudo().search([
                    ('holiday_status_id', 'in', origin_over_time_records.x_holiday_status_id.ids),
                    ('employee_id', '=', line.x_employee_id.id)
                ])
                total_allocated_hours = sum([float(
                    allocation.number_of_hours_display) for allocation in allocations] or [])
                total_remaining_hours = total_allocated_hours - total_validated_hours
                line.x_total_allocated_hours = total_allocated_hours
                line.x_total_validated_hours = total_validated_hours
                line.x_total_remaining_hours = total_remaining_hours
        except Exception as e:
            _logger.exception(msg=e)
            raise UserError(e)

    x_total_duration_by_group = fields.Binary(
        string="Total duration by group", compute="_compute_x_total_duration_by_group")

    def _get_working_uom_unit(self, uom_type):
        try:
            if uom_type == 'hour':
                return self.env.ref(xml_id='uom.product_uom_hour')
            if uom_type == 'day':
                return self.env.ref(xml_id='uom.product_uom_day')
            if uom_type == 'month':
                return self.env.ref(xml_id='enmasys_overtime.product_uom_month')
            return self.env['uom.uom']
        except Exception as e:
            _logger.exception(msg=e)

    @api.depends('x_over_time_report_detail_line_ids')
    def _compute_x_total_duration_by_group(self):
        try:
            for summary in self:
                if not summary.x_over_time_report_detail_line_ids:
                    summary.x_total_duration_by_group = False
                    continue
                total_text = _("Total of")
                datas = [
                    {dl.x_work_entry_type_id: dl.x_over_time_duration} for dl in
                    summary.x_over_time_report_detail_line_ids
                ]
                work_entry_types_and_total = {
                    k: sum(data.get(k, 0) for data in datas) for k in {key for dic in datas for key in dic}
                }
                total_by_group = []
                hour_working_uom = self._get_working_uom_unit(uom_type='hour')
                for group, total in work_entry_types_and_total.items():
                    total_by_group.append((
                        f"{total_text} {group.name}",
                        total,
                        total,
                        self.format_duration_group_by_work_entry_type(
                            self.env, total, uom_obj=hour_working_uom),
                        self.format_duration_group_by_work_entry_type(
                            self.env, total, uom_obj=hour_working_uom),
                        len(work_entry_types_and_total),
                        group.id
                    ))
                summary.x_total_duration_by_group = total_by_group
        except Exception as e:
            _logger.exception(msg=e)
            raise UserError(e)

    @classmethod
    def format_duration_group_by_work_entry_type(
            cls, env, value, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False, uom_obj=False):
        # NOTE:
        # copy logic from formatLang of function formatLang from odoo.tools.misc and edit for specify case
        """
            Assuming 'Account' decimal.precision=3:
                formatLang(value) -> digits=2 (default)
                formatLang(value, digits=4) -> digits=4
                formatLang(value, dp='Account') -> digits=3
                formatLang(value, digits=5, dp='Account') -> digits=5
        """
        NON_BREAKING_SPACE = u'\N{NO-BREAK SPACE}'
        if digits is None:
            digits = DEFAULT_DIGITS = 2
            if dp:
                decimal_precision_obj = env['decimal.precision']
                digits = decimal_precision_obj.precision_get(dp)
            elif currency_obj:
                digits = currency_obj.decimal_places

        if isinstance(value, str) and not value:
            return ''

        lang_obj = get_lang(env)

        res = lang_obj.format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)

        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = '%s%s%s' % (res, NON_BREAKING_SPACE, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = '%s%s%s' % (currency_obj.symbol, NON_BREAKING_SPACE, res)
        if uom_obj:
            res = '%s%s%s' % (res, NON_BREAKING_SPACE, uom_obj.name)
        return res

    def action_check_var(self):
        try:
            action = self.env['ir.actions.actions']._for_xml_id(
                full_xml_id='enmasys_overtime.overtime_report_detail_line_default_action')
            action['domain'] = [('id', 'in', self.x_over_time_report_detail_line_ids.ids)]
            action['context'] = dict(create=False, edit=False, search_default_group_by_working_type=True, expand=True)
            return action
        except Exception as e:
            _logger.exception(msg=e)
            raise ValueError(e)

    x_total_duration_group_by_working_type = fields.Html(
        string="Total Intervals", compute="_compute_x_total_duration_group_by_working_type")

    @api.depends('x_over_time_report_detail_line_ids')
    def _compute_x_total_duration_group_by_working_type(self):
        try:
            for summary in self:
                detail_lines = summary.x_over_time_report_detail_line_ids
                if not detail_lines:
                    summary.x_total_duration_group_by_working_type = str()
                    continue
                work_entry_types = list(set([
                    detail_line.x_work_entry_type_id for detail_line in detail_lines
                ]))
                work_entry_type_total = {
                    work_entry_type: (
                        len(list(set([detail_line.x_employee_id for detail_line in detail_lines.filtered(
                            lambda dl: dl.x_work_entry_type_id == work_entry_type)])) or []),
                        sum([detail_line.x_over_time_duration for detail_line in detail_lines.filtered(
                            lambda dl: dl.x_work_entry_type_id == work_entry_type)] or [])
                    )
                    for work_entry_type in work_entry_types
                }
                summary.x_total_duration_group_by_working_type = self._generate_work_entry_type_total_html(
                    datas=work_entry_type_total)
        except Exception as e:
            self._handle_exception(exception=e)

    @classmethod
    def _generate_work_entry_type_total_html(cls, datas):
        try:
            table = """
                        <table style="white-space: nowrap; color:#000000; font-family: sans-serif; font-size: 13px; border-collapse:collapse;">
                            {ROWS}
                        </table>
                        """
            tds = []
            quantity_employee_over_time_label = _("Total Employees")
            total_over_time_interval = _("Total OVER-TIME Intervals")
            for work_entry_type, totals in datas.items():
                tds.extend([
                    "<tr>",
                    f"""<td style="text-align: left;">{work_entry_type.name}</td>""",
                    f"""<td style="text-align: left; padding-right: 10px; padding-left: 10px;">
                                {quantity_employee_over_time_label}: {totals[0]}
                            </td>""",
                    f"""<td style="text-align: left; padding-right: 10px; padding-left: 10px;">
                                {total_over_time_interval}: {totals[1]}
                            </td>""",
                    "</tr>"
                ])
            return table.format(ROWS='\n'.join(tds))
        except Exception as e:
            cls._handle_exception(exception=e)