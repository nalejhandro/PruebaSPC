from odoo.tests import Form, TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestAccountMove(TransactionCase):
    """Test cases for Invoice and Journal entries customizations"""

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_5')
        self.action_inv_lines = self.env.ref('spc.action_invoice_line_tree1')
        self.company2 = self.env.ref('stock.res_company_1')

    def create_invoice(self, partner=None, inv_type='out_invoice', **line_kwargs):
        if partner is None:
            partner = self.partner
        invoice = Form(self.env['account.move'].with_context(default_type=inv_type))
        invoice.partner_id = partner
        invoice = invoice.save()
        self.create_inv_line(invoice, **line_kwargs)
        return invoice

    def create_inv_line(self, invoice, product=None, quantity=1, price=100):
        if product is None:
            product = self.product
        with Form(invoice) as inv:
            with inv.invoice_line_ids.new() as line:
                line.product_id = product
                line.quantity = quantity
                line.price_unit = price

    def create_invoice_to_country(self, inv_lines, company=None, sale_margin=10.0):
        """Create Customer invoice using the wizard 'Invoice to Country'"""
        ctx = {
            'active_model': inv_lines._name,
            'active_ids': inv_lines.ids,
        }
        if company is None:
            company = self.company2
        wizard = Form(self.env['account.invoice.create'].with_context(**ctx))
        wizard.partner_id = company.partner_id
        wizard = wizard.save()
        wizard_result = wizard.action_invoice_create()
        customer_invoice = self.env['account.move'].browse(wizard_result['res_id'])
        return customer_invoice

    def get_available_inv_lines_country(self):
        """Get invoice lines available in 'To be Invoiced to Country' List view"""
        domain = safe_eval(self.action_inv_lines.domain)
        available_inv_lines = self.env['account.move.line'].search(domain)
        return available_inv_lines

    def test_01_account_invoice_create(self):
        supplier_invoice = self.create_invoice(inv_type='in_invoice')
        price_unit = supplier_invoice.invoice_line_ids[0].price_unit
        sale_margin = 10.0
        expected_amount = (price_unit + (price_unit * (sale_margin / 100))) or 0.0

        # Check lines available in 'To be Invoiced to Country' List view, lines for the invoice
        # just created shouldn't be there, because the invoice is still in draft
        self.assertNotIn(
            supplier_invoice.invoice_line_ids,
            self.get_available_inv_lines_country())

        # Validate invoice and check lines again, they should now be there
        supplier_invoice.post()
        self.assertIn(
            supplier_invoice.invoice_line_ids,
            self.get_available_inv_lines_country())

        # Create Customer invoice using the wizard 'Invoice to Country'
        customer_invoice = self.create_invoice_to_country(supplier_invoice.invoice_line_ids)

        # Check if customer invoice has the expected amount
        self.assertEqual(customer_invoice.amount_untaxed, expected_amount,
                         "Unexpected invoice untaxed amount")

        # Check supplier invoice relationship with new invoice
        self.assertEqual(supplier_invoice.invoice_line_ids.line_dest_id,
                         customer_invoice.invoice_line_ids[0],
                         "New line should be related to the supplier invoice")

        # Once a customer invoice is created, lines shouldn't be available anymore in 'To be Invoiced to Country'
        self.assertNotIn(
            supplier_invoice.invoice_line_ids,
            self.get_available_inv_lines_country())
