from odoo import models, api


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super().create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        return res
