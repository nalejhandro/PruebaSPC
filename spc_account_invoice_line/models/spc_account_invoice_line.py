# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    # @api.multi
    # def invoice_validate(self):
    #     if self.type == "out_invoice":
    #         res = super(AccountInvoice, self).invoice_validate()
    #         if abs(self.amount_untaxed_not_discounted - self.subtotal_print)\
    #                 > 10:
    #             raise Warning(_('Subtotals are different.'))
    #         if abs(self.amount_tax - self.amount_tax_print) > 10:
    #             raise Warning(_('Taxes are different.'))
    #         if abs(self.amount_discounted - self.discount_print) > 10:
    #             raise Warning(_('Discount are different.'))
    #         if abs(self.amount_total - self.total_print) > 10:
    #             raise Warning(_('Totals are different.'))
    #     else:
    #         res = super(AccountInvoice, self).invoice_validate()
    #     return res

    # @api.multi
    # def button_copy_amounts(self):
    #     for invoice in self:
    #         invoice.write({
    #             'subtotal_print': invoice.amount_untaxed_not_discounted,
    #             'amount_tax_print': invoice.amount_tax,
    #             'discount_print': invoice.amount_discounted,
    #             'total_print': invoice.amount_total,
    #         })
    #     return True

    print_line_ids = fields.One2many('account.invoice.printlines',
                                     'invoice_id', string='Print Lines')
    subtotal_print = fields.Float('Subtotal',
                                  digits=dp.get_precision('Account'))
    total_print = fields.Float(string='Total',
                               digits=dp.get_precision('Account'))
    amount_tax_print = fields.Float(string='Tax',
                                    digits=dp.get_precision('Account'))
    discount_print = fields.Float('Discount',
                                  digits=dp.get_precision('Account'))


class AccountInvoicePrintlines(models.Model):
    """Print Lines"""

    _name = 'account.invoice.printlines'
    _description = __doc__

    invoice_id = fields.Many2one('account.invoice', string='Invoices')
    name = fields.Text('Description')
    quantity = fields.Float('Quant.')
    uos_id = fields.Many2one('product.uom', string='Unit of Measure',
                             ondelete='set null', index=True)
    invoice_line_tax_id = fields.Char(string='Taxes')
    discount = fields.Float()
    price_unit = fields.Float(string='Unit. Amount')
    price_subtotal = fields.Float(string='Total Amount', store=True)


# class AccountInvoiceLine(models.Model):
#
#     _inherit = 'account.invoice.line'
# """
#     @api.model
#     def create(self, vals):
#         res = super(AccountInvoiceLine, self).create(vals)
#         printlines_obj = self.env['account.invoice.printlines']
#         # Create the print lines for each account invoice line
#         if vals['invoice_line_tax_id']:
#             tax = "IV"
#         else:
#             tax = "Exc"
#         print_lines = {
#             'quantity': vals['quantity'],
#             'uos_id': vals['uos_id'],
#             'name': vals['name'],
#             'discount': vals['discount'] if 'discount' in vals.keys() else 0.0,
#             'invoice_line_tax_id': tax,
#             'price_unit': vals['price_unit'],
#             'price_subtotal': res.price_subtotal,
#             'invoice_id': res.invoice_id.id,
#         }
#         printlines_obj.create(print_lines)
#         return res
# """
