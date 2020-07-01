# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(AccountAnalyticAccount, self).create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        return res


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        return res
