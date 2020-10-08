# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    date_stage_change = fields.Datetime(
        'Fecha de último cambio de etapa',
        readonly=True
    )

    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_stage_change'] = datetime.now()
        return super(CrmLead, self).write(vals)
