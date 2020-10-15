from datetime import datetime
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_stage_change = fields.Datetime(
        'Date of last stage update',
        readonly=True
    )

    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_stage_change'] = datetime.now()
        return super(ProjectTask, self).write(vals)
