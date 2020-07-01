# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    line_dest_id = fields.Many2one(
        'account.invoice.line',
        string='Downstream Line',
        readonly=True,
        help="It's filled, it's because a customer invoice line was generated"
        " from this line."
    )
    invoice_dest_id = fields.Many2one(
        'account.invoice',
        related='line_dest_id.invoice_id',
        string='Downstream Invoice',
        readonly=True,
        help="It's filled, it's because a customer invoice line was generated"
        " from this line."
    )
