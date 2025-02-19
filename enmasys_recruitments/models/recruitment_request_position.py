import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..recruitment_recruitment import MALE_GENDER, FEMALE_GENDER

_logger = logging.getLogger(__name__)


class RecruitmentRequestPosition(models.Model):
    _name = "recruitment.request.position"
    _description = "Recruitment Request: Position"
    _rec_name = "x_working_position_id"

    # inverse_name
    x_request_id = fields.Many2one(comodel_name="recruitment.request", string="Recruitment Request", ondelete="cascade")

    # in4
    x_working_position_id = fields.Many2one(comodel_name="hr.job", string="Working Position", required=True)
    x_gender_recruitment = fields.Selection(
        selection=[(MALE_GENDER, "Male"), (FEMALE_GENDER, "Female")], string="Gender requirement")
    x_salary_min = fields.Float(string="Salary min", )
    x_salary_max = fields.Float(string="Salary max", )
    x_receivable_salary_type = fields.Selection(
        selection=[('per_day', "Per day"), ('per_month', "Per month")], string="Receivable Salary-type",
        default='per_month', )
    x_currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", default=lambda self: self.env.company.currency_id.id)
    x_working_location = fields.Char(string="Working Location", )
    x_contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract type")
    x_contract_interval = fields.Float(string="Contract Interval")
    x_applicant_exp_requirement = fields.Float(string="Applicant Experience requirement")
    x_responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible")
    x_take_note = fields.Char(string="Taking note", )
    x_resources_requirement = fields.Integer(string="Resources Requirement", )

    def generate_recruitment_position_vals(self):
        try:
            vals = []
            for request_position in self:
                vals.append({
                    'x_working_position_id': request_position.x_working_position_id.id,
                    'x_recruitment_id': request_position.x_request_id.id,
                    'x_request_position_id': request_position.id,
                    'x_working_location': request_position.x_working_location,
                    'x_reference_date': request_position.x_request_id.x_reference_date,
                    'x_resources_requirement': request_position.x_resources_requirement,
                    'x_salary_min': request_position.x_salary_min,
                    'x_salary_max': request_position.x_salary_max,
                    'x_receivable_salary_type': request_position.x_receivable_salary_type,
                    'x_recruiter_id': self.env.user.employee_id.id,
                    'x_gender_requirement': request_position.x_gender_recruitment
                })
            return vals
        except Exception as e:
            _logger.exception(msg=e)
            raise ValidationError(e)

