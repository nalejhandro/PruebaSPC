# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    # Many to one relationship with account.analytic.account for welcome_kits
    wk_contract_id = fields.Many2one("account.analytic.account",
                                     string="Contract")
