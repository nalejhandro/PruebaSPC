# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.multi
    def get_cost_sale_order(self):
        for line in self:
            # Lines created after installing the stock_account_move_line
            if line.stock_picking_id and \
                    line.stock_picking_id.cost_sale_order_id and \
                    line.account_id.cost_on_sale_order and \
                    line.stock_picking_id.company_id.id == line.company_id.id:
                line.cost_sale_order_id = \
                    line.stock_picking_id.cost_sale_order_id
            # lines created before installing the stock_account_move_line
            elif not line.stock_picking_id and line.product_id and \
                    line.account_id.cost_on_sale_order:
                stock_move_obj = self.env['stock.move']
                stock_move_ids = stock_move_obj.search(
                    [('product_id', '=', line.product_id.id),
                     ('product_uom_qty', '=', line.quantity),
                     ('picking_id.name', '=', line.ref),
                     ('company_id', '=', line.company_id.id)], limit=1)
                if stock_move_ids:
                    picking = stock_move_ids.picking_id
                    line.picking_id = stock_move_ids.picking_id
                    line.cost_sale_order_id = picking.cost_sale_order_id
                else:
                    line.cost_sale_order_id = False
            else:
                line.cost_sale_order_id = False

    cost_sale_order_id = fields.Many2one(
        'sale.order', string='Cost Sale Order')
