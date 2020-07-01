# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    def _prepare_account_move_line(
            self, cr, uid, move, qty, cost, credit_account_id,
            debit_account_id, context=None):
        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context=context)

        if move.picking_id.cost_sale_order_id:
            debit_line_vals = res[0][2]
            credit_line_vals = res[1][2]
            picking = move.picking_id
            account_obj = self.pool.get('account.account')

            debit_acc_id = debit_line_vals['account_id']
            debit_acc = account_obj.browse(
                cr, uid, debit_acc_id, context=context)
            if debit_acc.cost_on_sale_order:
                debit_line_vals.update({
                    'cost_sale_order_id': picking.cost_sale_order_id.id,
                })
            credit_acc_id = credit_line_vals['account_id']
            credit_acc = account_obj.browse(
                cr, uid, credit_acc_id, context=context)
            if credit_acc.cost_on_sale_order:
                credit_line_vals.update({
                    'cost_sale_order_id': picking.cost_sale_order_id.id,
                })
            return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
