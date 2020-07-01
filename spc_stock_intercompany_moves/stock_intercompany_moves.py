# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import copy
from openerp import models, api
from openerp.tools.float_utils import float_compare
from openerp import SUPERUSER_ID


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.model
    def _quants_get_order(
            self, location, product, quantity, domain=None, orderby='in_date'):
        if not domain:
            domain = []
        domain2 = copy.copy(domain)
        res = super(StockQuant, self)._quants_get_order(
            location, product, quantity, domain=domain, orderby=orderby)
        if res and res[0][0] is None:
            if location and location.usage == 'transit':
                domain2 += location and [
                    ('location_id', 'child_of', location.id)
                ] or []
                domain2 += [('product_id', '=', product.id)]
                res = []
                offset = 0
                while float_compare(
                        quantity, 0,
                        precision_rounding=product.uom_id.rounding) > 0:
                    quants = self.search(
                        domain2, order=orderby, limit=10, offset=offset)
                    if not quants:
                        res.append((None, quantity))
                        break
                    for quant in quants:
                        rounding = product.uom_id.rounding
                        if float_compare(
                                quantity, abs(quant.qty),
                                precision_rounding=rounding) >= 0:
                            res += [(quant, abs(quant.qty))]
                            quantity -= abs(quant.qty)
                        elif float_compare(
                                quantity, 0.0,
                                precision_rounding=rounding) != 0:
                            res += [(quant, quantity)]
                            quantity = 0
                            break
                    offset += 10
        return res

    def _quant_split(self, cr, uid, quant, qty, context=None):
        res = super(StockQuant, self)._quant_split(
                                        cr, uid, quant, qty, context=None)
        if 'transit_company_id' in context:
            self.write(
                cr, SUPERUSER_ID, quant.id, {
                    'company_id': context['transit_company_id']},
                context=context)
        return res

    def quants_move(self, cr, uid, quants, move, location_to,
                    location_from=False, lot_id=False, owner_id=False,
                    src_package_id=False, dest_package_id=False, context=None):
        if move.location_dest_id.usage == 'transit':
            if not context:
                context = {}
            if move.partner_id.ref_companies:
                ctx = context.copy()
                ctx.update({
                    'transit_company_id': move.partner_id.ref_companies.id
                })
                return super(StockQuant, self).quants_move(
                    cr, uid, quants, move, location_to,
                    location_from=location_from, lot_id=lot_id,
                    owner_id=owner_id, src_package_id=src_package_id,
                    dest_package_id=dest_package_id, context=ctx)
        return super(StockQuant, self).quants_move(
                    cr, uid, quants, move, location_to,
                    location_from=location_from, lot_id=lot_id,
                    owner_id=owner_id, src_package_id=src_package_id,
                    dest_package_id=dest_package_id, context=context)


class StockMove(models.Model):

    _inherit = 'stock.move'

    def quants_reserve(self, cr, uid, quants, move, link=False, context=None):
        if move.location_dest_id.usage == 'transit':
            if not context:
                context = {}
            if move.partner_id.ref_companies:
                ctx = context.copy()
                ctx.update({
                    'transit_company_id': move.partner_id.ref_companies.id
                })
                return super(StockMove, self).quants_reserve(
                    cr, uid, quants, move, link=link, context=ctx)
        return super(StockMove, self).quants_reserve(
                    cr, uid, quants, move, link=link, context=context)

    def force_assign(self, cr, uid, ids, context=None):
        """ Changes the state to assigned if the
        source location usage is not transit.
        @return: True
        """
        move_ids = []
        if context and context.get('force_transit', False):
            move_ids = ids
        else:
            # Remove moves from transit locations
            for move in self.browse(cr, uid, ids, context=context):
                if move.location_id.usage != 'transit':
                    move_ids.append(move.id)
        return super(StockMove, self).force_assign(
            cr, uid, move_ids, context=context)

    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        if context is None:
            context = {}
        if type in ('in_invoice', 'in_refund') and \
                move_line.location_id.usage == 'transit':
            if move_line.partner_id and \
                    move_line.partner_id.property_product_pricelist_purchase:
                pricelist_obj = self.pool.get("product.pricelist")
                pricelist = move_line.partner_id.property_product_pricelist_purchase.id
                price = pricelist_obj.price_get(
                    cr, uid, [pricelist], move_line.product_id.id,
                    move_line.product_uom_qty,
                    move_line.partner_id.id)[pricelist]
                if price:
                    return price
        return super(StockMove, self)._get_price_unit_invoice(
            cr, uid, move_line, type, context=context)
