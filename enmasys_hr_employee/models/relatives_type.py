from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RelativesType(models.Model):
    _name = "relatives.type"

    name = fields.Char('Loại quan hệ', required=True)
