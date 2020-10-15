from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountInvoiceCreate(models.TransientModel):
    """Create invoices from multiple invoice lines"""

    _name = "account.invoice.create"
    _description = "Create Invoice"

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
        default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(
        string='Base amount',
        currency_field='currency_id',
        compute='_compute_amount',
        store=True)
    invoice_line_ids = fields.Many2many(
        'account.move.line',
        string='Invoice Lines',
        copy=False)

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

    @api.model
    def _domain_partner_id(self):
        all_companies = self.env['res.company'].sudo().search([])
        default_domain = [('is_company', '=', True)]
        partner_ids = []
        if all_companies:
            companies = all_companies - self.env.company
            partner_ids = companies.partner_id.ids
        return [('id', 'in', partner_ids)] if partner_ids else default_domain

    @api.model
    def default_get(self, field_list):
        res = super(AccountInvoiceCreate, self).default_get(field_list)
        active_ids = self._context.get('active_ids')
        assert active_ids, "Programming error: wizard action executed without active_ids"
        res.update({
            'invoice_line_ids': [(6, 0, active_ids)]
        })
        return res

    def _prepare_invoice(self):
        """ Prepare the dict of values to create the new invoice from a selected invoice lines.
        """
        self.ensure_one()
        journal_id = self.env['account.move'].with_context(default_type='out_invoice').default_get(
            ['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))

        company = self.env.company
        values = {
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': journal_id,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'company_id': company.id,
        }

        if company.invoice_terms:
            values['note'] = company.with_context(lang=self.partner_id.lang).invoice_terms
        if self.partner_id.user_id:
            values['user_id'] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id

        return values

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

        res = line.copy_data({
            'price_unit': price_unit,
            'account_id': account.id,
            'move_id': invoice.id,
        })[0]
        return res

    def action_invoice_create(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        invoice = self.env['account.move'].create(self._prepare_invoice())
        for line in self.invoice_line_ids:
            if not float_is_zero(line.quantity, precision_digits=precision):
                invoice.invoice_line_ids = [(0, 0, self._prepare_invoice_line(line, invoice))]
                line.line_dest_id = invoice.invoice_line_ids.sorted('id')[-1]
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action.update({
            'views': [v for v in action['views'] if v[1] == 'form'],
            'res_id': invoice.id,
        })
        return action
