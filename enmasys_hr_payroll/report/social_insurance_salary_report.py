import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SocialInsuranceSalaryReport(models.TransientModel):
    _name = "social.insurance.salary.report"
    _description = "Social Insurance Report: Salary"

    # inverse_name
    x_report_id = fields.Many2one(
        comodel_name="social.insurance.report", string="Social Insurance Report", ondelete="cascade")

    # in4
    x_employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    x_contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    x_social_insurance_no = fields.Char(string="Social Insurance No.")
    x_first_contract_date = fields.Date(string="First contract date")
    x_contract_wage = fields.Float(string="Wage")
    x_currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", related="x_contract_id.currency_id")
    x_seniority_wage = fields.Float(string="Seniority wage")
    x_social_insurance_wage = fields.Float(string="Social Insurance wage")
    x_medical_insurance_wage = fields.Float(string="Medical Insurance wage")
    x_unemployment_insurance_wage = fields.Float(string="Unemployment Insurance wage")
    x_social_insurance_by_employee_wage = fields.Float(string="Contributed Social-Insurance wage by employee")
    x_medical_insurance_by_employee_wage = fields.Float(string="Contributed Medical-Insurance wage by employee")
    x_unemployment_insurance_by_employee_wage = fields.Float(
        string="Contributed Unemployment-Insurance wage by employee")
    x_social_insurance_by_company_wage = fields.Float(string="Contributed Social-Insurance wage by Company")
    x_medical_insurance_by_company_wage = fields.Float(string="Contributed Medical-Insurance wage by Company")
    x_unemployment_insurance_by_company_wage = fields.Float(string="Contributed Unemployment-Insurance wage by Company")
