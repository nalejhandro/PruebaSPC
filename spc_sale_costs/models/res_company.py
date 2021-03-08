from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    company_user_id = fields.Many2one("res.company", help="User Company for SPC",)
    user_group_id = fields.Many2one("res.groups", help="User group for SPC",)
