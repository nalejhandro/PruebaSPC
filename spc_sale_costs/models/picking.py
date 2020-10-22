# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def get_cost_sale_order(self):
        for picking in self:
            if picking.picking_type_id.cost_on_sale_order:
                picking.cost_sale_order_id = self.env['sale.order'].search(
                    [('procurement_group_id', '=', picking.group_id.id),
                     ('company_id', '=', picking.company_id.id)],
                    limit=1)
            else:
                picking.cost_sale_order_id = False
            self.env['account.move.line'].search(
                [('stock_picking_id', '=', picking.id)]).get_cost_sale_order()
            # lines created before installing the stock_account_move_line
            self.env['account.move.line'].search([
                ('ref', '=', picking.name),
                ('company_id', '=', picking.company_id.id),
                ('stock_picking_id', '=', False),
            ]).get_cost_sale_order()

    cost_sale_order_id = fields.Many2one(
        'sale.order', string='Cost Sale Order')

    @api.model
    def create(self, vals):
        if 'picking_type_id' in vals and 'group_id' in vals and \
                'company_id' in vals:
            picking_type = self.env['stock.picking.type'].search(
                [('id', '=', vals['picking_type_id'])])
            if picking_type.cost_on_sale_order:
                sale_order = self.env['sale.order'].search(
                    [('procurement_group_id', '=', vals['group_id']),
                     ('company_id', '=', vals['company_id'])],
                    limit=1)
                vals['cost_sale_order_id'] = sale_order.id
            else:
                vals['cost_sale_order_id'] = False
        return super(StockPicking, self).create(vals)

    def write(self, vals):
        for picking in self:
            picking_type_id = vals.get('picking_type_id') or picking.picking_type_id.id
            group_id = vals.get('group_id') or picking.group_id.id
            company_id = vals.get('company_id') or picking.company_id.id
            picking_type = self.env['stock.picking.type'].search([('id', '=', picking_type_id)])
            if picking_type.cost_on_sale_order:
                sale_order = self.env['sale.order'].search([
                    ('procurement_group_id', '=', group_id),
                    ('company_id', '=', company_id)], limit=1)
                vals['cost_sale_order_id'] = sale_order.id or False
            else:
                vals['cost_sale_order_id'] = False
            super(StockPicking, picking).write(vals)
        return True
