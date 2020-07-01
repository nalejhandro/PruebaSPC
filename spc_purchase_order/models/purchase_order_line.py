# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields, api
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_categ_id = fields.Many2one(
        related='product_id.categ_id',
        readonly=True,
        store=True
        )
    order_partner_ref = fields.Char(
        related='order_id.partner_ref',
        readonly=True
        )
    order_requisition_id = fields.Many2one(
        related='order_id.requisition_id',
        readonly=True
        )
    compute_invoiced = fields.Boolean(
        'Invoiced',
        compute='_compute_line_status',
        readonly=True,
        store=True
        )
    compute_received = fields.Boolean(
        'Received',
        compute='_compute_line_status',
        readonly=True,
        store=True
        )
    compute_delivered = fields.Boolean(
        'Delivered',
        compute='_compute_line_status',
        readonly=True,
        store=True
        )
    compute_invoiced_qty = fields.Float(
        'Invoiced qty.',
        compute='_compute_line_status',
        readonly=True,
        store=True,
        digits=dp.get_precision('Product Unit of Measure')
        )
    compute_received_qty = fields.Float(
        'Received qty.',
        compute='_compute_line_status',
        readonly=True,
        store=True,
        digits=dp.get_precision('Product Unit of Measure')
        )
    compute_delivered_qty = fields.Float(
        'Delivered qty.',
        compute='_compute_line_status',
        readonly=True,
        store=True,
        digits=dp.get_precision('Product Unit of Measure')
        )

    @api.depends('invoice_lines.invoice_id.state', 'move_ids.state', 'order_id.state')
    def _compute_line_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for record in self:
            invoiced = False
            received = False
            delivered = False
            invoiced_qty = 0.0
            received_qty = 0.0
            delivered_qty = 0.0
            for line in record.invoice_lines:
                if line.invoice_id.state in ('open', 'paid'):
                    invoiced_qty += line.quantity
            if float_compare(record.product_qty, invoiced_qty, precision_digits=precision) == 0:
                invoiced = True
            for move in record.move_ids:
                if move.state == 'done':
                    received_qty += move.product_uom_qty
                # TODO: Set delivered quantity, no quants in v11
                # for quant in move.quant_ids:
                #     if quant.location_id.usage != 'internal' or quant.location_id.company_id != move.company_id:
                #         delivered_qty += quant.qty

            if float_compare(record.product_qty, received_qty, precision_digits=precision) == 0:
                received = True
            if float_compare(record.product_qty, delivered_qty, precision_digits=precision) == 0:
                delivered = True

            record.compute_invoiced = invoiced
            record.compute_received = received
            record.compute_delivered = delivered
            record.compute_invoiced_qty = invoiced_qty
            record.compute_received_qty = received_qty
            record.compute_delivered_qty = delivered_qty
