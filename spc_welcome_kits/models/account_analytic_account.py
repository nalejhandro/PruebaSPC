# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class AccountAnayliticAccount(models.Model):

    _inherit = "account.analytic.account"

    # New field in contract
    wk_production_lot_ids = fields.One2many(
        "stock.production.lot", "wk_contract_id", string="Production Lot",
        domain=[('wk_contract_id', '=', 'False')])
