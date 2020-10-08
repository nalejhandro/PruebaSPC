# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    date_stage_change = fields.Datetime(
        'Fecha de último cambio de etapa',
        readonly=True
    )

    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_stage_change'] = datetime.now()
        return super(HelpdeskTicket, self).write(vals)
