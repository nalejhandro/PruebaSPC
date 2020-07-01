# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountInvoiceCreate(models.TransientModel):
    """Create invoices from multiple invoice lines"""

    _name = "account.invoice.create"
    _description = "Create Invoice"

    @api.depends('partner_id')
    def _compute_amount(self):
        total = 0
        if self.partner_id:
            for line in self.invoice_line_ids:
                price = line.price_subtotal
                sale_margin = self.sale_margin or 0.0
                price = (price + (price * (sale_margin / 100))) or 0.0
                total += price
        self.amount = total

    def _domain_partner_id(self):
        all_companies = self.env['res.company'].sudo().search([])
        default_domain = [('is_company', '=', True), ('customer', '=', True)]
        partner_ids = []
        if all_companies:
            companies = all_companies - self.env.user.company_id
            partner_ids = companies.mapped('partner_id').ids
        return [('id', 'in', partner_ids)] if partner_ids else default_domain

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        domain=lambda self: self._domain_partner_id(),
        help="Partner to be invoiced")
    sale_margin = fields.Float(
        related='partner_id.property_sale_margin',
        readonly=True,
        help="Sale margin configured in selected partner")
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(
        string='Base amount',
        currency_field='currency_id',
        compute='_compute_amount',
        readonly=True, store=True)
    invoice_line_ids = fields.Many2many(
        'account.invoice.line',
        string='Invoice Lines',
        copy=False)

    @api.model
    def default_get(self, field_list):
        res = super(AccountInvoiceCreate, self).default_get(field_list)
        active_ids = self._context.get('active_ids')

        # Check for selected invoice lines ids
        if not active_ids:
            raise UserError(
                _("Programming error: wizard action executed without active_ids"
                  " in context."))

        invoice_lines = self.env['account.invoice.line'].browse(active_ids)

        res.update({
            'invoice_line_ids': [(6, 0, invoice_lines.ids)]
        })

        return res

    @api.multi
    def _prepare_invoice(self):
        """ Prepare the dict of values to create the new invoice from a selected invoice lines.
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))

        values = {
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': journal_id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'company_id': self.env.user.company_id.id,
        }

        if self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner.lang).env.user.company_id.sale_note
        if self.partner_id.user_id:
            values['user_id'] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id

        return values

    @api.multi
    def _prepare_invoice_line(self, line, invoice):
        """ Prepare the dict of values to create the new invoice line
        :param line: source account invoice line
        """
        self.ensure_one()

        account = (
            line.product_id.property_account_income_id or
            line.product_id.categ_id.property_account_income_categ_id or
            self.env['ir.property'].get('property_account_income_categ_id', 'product.category'))

        if not account and line.product_id:
            raise UserError(
                _('Please define income account for this product: '
                  '"%s" (id:%d) - or for its category: "%s".') % (
                      line.product_id.name, line.product_id.id,
                      line.product_id.categ_id.name))

        fpos = invoice.fiscal_position_id
        if fpos and account:
            account = fpos.map_account(account)

        price_unit = line.price_unit
        sale_margin = self.sale_margin or 0.0
        price_unit = (price_unit + (price_unit * (sale_margin / 100))) or 0.0

        res = {
            'name': line.name,
            'sequence': line.sequence,
            'origin': line.invoice_id.number,
            'price_unit': price_unit,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'product_id': line.product_id.id or False,
            'account_id': account.id,
            'invoice_id': invoice.id,
            'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, line.invoice_line_tax_ids.ids)],
        }
        return res

    @api.multi
    def action_invoice_create(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if not self.partner_id:
            raise UserError(_('You must first select a partner!'))
        invoice = self.env['account.invoice'].create(self._prepare_invoice())
        for line in self.invoice_line_ids:
            if not float_is_zero(line.quantity, precision_digits=precision):
                new_line = self.env['account.invoice.line'].create(
                    self._prepare_invoice_line(line, invoice))
                line.write({'line_dest_id': new_line.id})
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = invoice.id
        return action
