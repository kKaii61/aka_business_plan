import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..recruitment_recruitment import (
    IN_REQUEST_STATUS, IN_RECRUIT_STATUS, CANCELLED_STATUS, DONE_STATUS, RECRUITMENT_STATUSES)

_logger = logging.getLogger(__name__)


class RecruitmentRequest(models.Model):
    _name = "recruitment.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Recruitment Request"
    _rec_name = "x_reference_no"
    _order = "create_date desc"

    x_reference_no = fields.Char(string="Reference No.", default="YCTD/", readonly=True, tracking=True)
    x_reference_date = fields.Date(string="Reference Date", required=True, default=fields.Date.today(), tracking=True)
    x_recruit_department_id = fields.Many2one(comodel_name="hr.department", string="Recruit Department", tracking=True)
    state = fields.Selection(selection=RECRUITMENT_STATUSES, string="Status", default=IN_REQUEST_STATUS, tracking=True)
    x_working_location = fields.Char(string="Working Location", tracking=True, required=True)
    x_request_position_ids = fields.One2many(
        comodel_name="recruitment.request.position", string="Request Positions", inverse_name="x_request_id")

    @api.model
    def create(self, vals):
        try:
            new_request = super(RecruitmentRequest, self).create(vals)
            sequences = new_request.generate_sequences(fields=['x_reference_no'])
            for field, sequence in sequences.items():
                new_request[field] = sequence
            return new_request
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def generate_sequences(self, fields):
        try:
            sequences = dict()
            for field in fields:
                sequences[field] = self.get_sequence(field=field)
            return sequences
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def get_sequence(self, field):
        try:
            if field == 'x_reference_no':
                return self.generate_reference_no(ref_date=self.x_reference_date)
            return str()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def generate_reference_no(self, ref_date):
        try:
            ref_no = str()
            sequence = self.env.ref(
                xml_id='enmasys_recruitments.recruitment_request_x_reference_no_sequence', raise_if_not_found=False)
            if not ref_date or not sequence:
                return ref_no
            _sequence = sequence.sudo()
            _sequence_prefix = _sequence.prefix or "YCTD"
            _next_sequence = _sequence.next_by_code(sequence_code=_sequence.code, sequence_date=ref_date)
            return "%(_prefix)s/%(_year)s/%(_suffix)s" % {
                '_prefix': _sequence_prefix, '_year': ref_date.year,
                '_suffix': _next_sequence.split(_sequence_prefix)[1]
            }
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    @api.model
    def unlink(self):
        try:
            if self.filtered(lambda rr: rr.state == 'done'):
                raise ValidationError(_("You cant delete any requests which is in Done state. Please check again."))
            return super(RecruitmentRequest, self).unlink()
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def must_have_at_least_position_request(self):
        if not self.x_request_position_ids:
            raise ValidationError(_("Make sure at least Position Request. Please check again."))

    def start_recruitments(self):
        try:
            for recruitment in self:
                # check already
                recruitment.must_have_at_least_position_request()
                # set state finally
                recruitment.state = IN_RECRUIT_STATUS
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def cancel_recruitments(self):
        try:
            for recruitment in self:
                recruitment.state = CANCELLED_STATUS
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def done_recruitments(self):
        try:
            for recruitment in self:
                recruitment.state = DONE_STATUS
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def teleport_to_working_positions(self):
        try:
            self.ensure_one()
            action = self.env['ir.actions.actions']._for_xml_id(full_xml_id='hr_recruitment.action_hr_job')
            action['domain'] = [('id', 'in', self.x_request_position_ids.x_working_position_id.ids)]
            action['context'] = {
                'create': bool(self.state in ['in_request', 'in_recruit']),
                'edit': bool(self.state in ['in_request', 'in_recruit']),
                'belong_recruitment_request': self.id
            }
            return action
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    x_working_positions_quantity = fields.Integer(
        string="Working Position quantity", compute="_compute_x_working_positions_quantity", store=True)

    @api.depends('x_request_position_ids')
    def _compute_x_working_positions_quantity(self):
        try:
            for request in self:
                request.x_working_positions_quantity = len(request.x_request_position_ids.x_working_position_id)
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    x_applicants_in_recruitment_ids = fields.One2many(
        comodel_name="hr.applicant", string="Applicants in Recruitment Request",
        inverse_name="x_recruitment_request_id")

    x_applicants_in_recruitment_qty = fields.Integer(
        string="Applicants quantity", compute="_compute_x_applicants_in_recruitment_qty", store=True)

    @api.depends('x_applicants_in_recruitment_ids')
    def _compute_x_applicants_in_recruitment_qty(self):
        try:
            for request in self:
                request.x_applicants_in_recruitment_qty = len(request.x_applicants_in_recruitment_ids)
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

    def teleport_to_recruit_applicants(self):
        try:
            self.ensure_one()
            action = self.env['ir.actions.actions']._for_xml_id(
                full_xml_id='hr_recruitment.crm_case_categ0_act_job')
            action['domain'] = [('id', 'in', self.x_applicants_in_recruitment_ids.ids)]
            action['context'] = {
                'create': bool(self.state in ['in_request', 'in_recruit']),
                'edit': bool(self.state in ['in_request', 'in_recruit']),
                'belong_recruitment_request': self.id
            }
            return action
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)
