# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_exempt_amount(self):
        exempt_amount = 0.0
        for line in self.invoice_line:
                if line.invoice_line_tax_id.amount == 0.0:
                    exempt_amount += line.price_subtotal
        self.exempt_amount = exempt_amount

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_tax_amount(self):
        tax_amount = 0.0
        for line in self.invoice_line:
                if line.invoice_line_tax_id.amount != 0.0:
                    tax_amount += line.price_subtotal
        self.tax_amount = tax_amount

    exempt_amount = fields.Float(string="Exempt Amount",
                                 compute='_compute_exempt_amount')
    tax_amount = fields.Float("Tax amount", compute='_compute_tax_amount')
