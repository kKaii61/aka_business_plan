import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

OVERTIME_INTERVALS = [
    ('0', '12:00 AM'), ('0.5', '12:30 AM'),
    ('1', '1:00 AM'), ('1.5', '1:30 AM'),
    ('2', '2:00 AM'), ('2.5', '2:30 AM'),
    ('3', '3:00 AM'), ('3.5', '3:30 AM'),
    ('4', '4:00 AM'), ('4.5', '4:30 AM'),
    ('5', '5:00 AM'), ('5.5', '5:30 AM'),
    ('6', '6:00 AM'), ('6.5', '6:30 AM'),
    ('7', '7:00 AM'), ('7.5', '7:30 AM'),
    ('8', '8:00 AM'), ('8.5', '8:30 AM'),
    ('9', '9:00 AM'), ('9.5', '9:30 AM'),
    ('10', '10:00 AM'), ('10.5', '10:30 AM'),
    ('11', '11:00 AM'), ('11.5', '11:30 AM'),
    ('12', '12:00 PM'), ('12.5', '12:30 PM'),
    ('13', '1:00 PM'), ('13.5', '1:30 PM'),
    ('14', '2:00 PM'), ('14.5', '2:30 PM'),
    ('15', '3:00 PM'), ('15.5', '3:30 PM'),
    ('16', '4:00 PM'), ('16.5', '4:30 PM'),
    ('17', '5:00 PM'), ('17.5', '5:30 PM'),
    ('18', '6:00 PM'), ('18.5', '6:30 PM'),
    ('19', '7:00 PM'), ('19.5', '7:30 PM'),
    ('20', '8:00 PM'), ('20.5', '8:30 PM'),
    ('21', '9:00 PM'), ('21.5', '9:30 PM'),
    ('22', '10:00 PM'), ('22.5', '10:30 PM'),
    ('23', '11:00 PM'), ('23.5', '11:30 PM')
]


class InheritResCompany(models.Model):
    _inherit = "res.company"
    _name = "res.company"

    x_over_time_lunch_from = fields.Float(string="Lunch from (HH:MM)", default=12)
    x_over_time_lunch_to = fields.Float(string="Lunch to (HH:MM)", default=13.5)

    x_default_estimated_ot_start_time = fields.Selection(
        selection=OVERTIME_INTERVALS, string="Default Overtime estimated start", default='7.5')
    x_default_estimated_ot_end_time = fields.Selection(
        selection=OVERTIME_INTERVALS, string="Default Overtime estimated end", default='17')
