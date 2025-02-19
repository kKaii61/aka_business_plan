import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InheritHrApplicant(models.Model):
    _inherit = "hr.applicant"

    x_recruitment_request_id = fields.Many2one(comodel_name="recruitment.request", string="Belong Recruitment Request")