from datetime import datetime
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    date_stage_change = fields.Datetime(
        'Date of last stage update',
        readonly=True
    )

    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_stage_change'] = datetime.now()
        return super(CrmLead, self).write(vals)
