# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Account(models.Model):

    _inherit = 'account.account'

    income_on_sale_order = fields.Boolean('Income on Sale Orders')
    cost_on_sale_order = fields.Boolean('Cost on Sale Orders')

    def write(self, vals):
        res = super().write(vals)
        for account in self:
            self.env['account.move.line'].search(
                [('account_id', '=', account.id)]).get_cost_sale_order()
        return res
