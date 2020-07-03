# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PickingType(models.Model):

    _inherit = 'stock.picking.type'

    cost_on_sale_order = fields.Boolean('Cost on Sale Orders')

    @api.model
    def create(self, vals):
        res = super(PickingType, self).create(vals)
        if 'cost_on_sale_order' in vals:
            self.env['stock.picking'].search(
                [('picking_type_id', '=', res.id)]).get_cost_sale_order()
        return res

    @api.multi
    def write(self, vals):
        res = super(PickingType, self).write(vals)
        for picking_type in self:
            if 'cost_on_sale_order' in vals:
                self.env['stock.picking'].search(
                    [('picking_type_id', '=', picking_type.id)]
                ).get_cost_sale_order()
        return res
