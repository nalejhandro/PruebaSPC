# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.model
    def create(self, vals):
        # Test if user is in config company (company_user_id) and if user is part of the
        # import group (user_group_id). If it is, a sudo is necesary as it will go
        # change records on other companies
        if (
            vals["company_id"] != self.env.user.company_id.id
            and self.env.user.company_id.user_group_id.id
            in self.env.user.groups_id._ids
            and self.env.user.company_id.id
            == self.env.user.company_id.company_user_id.id
        ):
            res = super(StockMove, self.sudo()).create(vals)
        else:
            res = super(StockMove, self.sudo()).create(vals)
        if "group_id" in vals and "picking_id" in vals:
            picking = self.env["stock.picking"].search(
                [("id", "=", vals["picking_id"])]
            )
            picking.sudo().get_cost_sale_order()
        return res

    def write(self, vals):
        # Test if user is in config company (company_user_id) and if user is part of the
        # import group (user_group_id). If it is, a sudo is necesary as it will go
        # change records on other companies
        if (
            self.env.user.company_id.id not in self.mapped("company_id.id")
            and self.env.user.company_id.user_group_id.id
            in self.env.user.groups_id._ids
            and self.env.user.company_id.id
            == self.env.user.company_id.company_user_id.id
        ):
            res = super(StockMove, self.sudo()).write(vals)
        else:
            res = super(StockMove, self.sudo()).write(vals)
        if "group_id" in vals or "picking_id" in vals:
            picking_obj = self.env["stock.picking"]
            for move in self:
                # picking_id = 'picking_id' in vals and vals['picking_id'] or move.picking_id.id
                picking_id = (
                    vals["picking_id"] if "picking_id" in vals else move.picking_id.id
                )
                picking = picking_obj.search([("id", "=", picking_id)])
                picking.sudo().get_cost_sale_order()
        return res
