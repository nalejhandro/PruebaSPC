from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_user_id = fields.Many2one(
        related="company_id.company_user_id", readonly=False
    )
    user_group_id = fields.Many2one(related="company_id.user_group_id", readonly=False)
