# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestAccountInvoice(TransactionCase):
    """Test cases for Invoice customizations"""

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.tax_model = self.env['account.tax']
        self.acc_analytic_model = self.env['account.analytic.account']
        self.acc_account_model = self.env['account.account']
        self.type_rec = self.env.ref('account.data_account_type_receivable')
        self.type_exp = self.env.ref('account.data_account_type_expenses')

    def create_supplier_invoice(self):
        tax = self.tax_model.create({
            'name': 'Tax 10.0',
            'amount': 10.0,
            'amount_type': 'fixed',
        })
        analytic_account = self.acc_analytic_model.create({'name': 'test account'})

        invoice = self.invoice_model.create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'type': 'in_invoice',
        })
        self.assertEquals(invoice.journal_id.type, 'purchase')

        invoice_line_account = self.acc_account_model.search([
            ('user_type_id', '=', self.type_exp.id)], limit=1).id

        self.invoice_line_model.create({
            'product_id': self.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
            'name': 'product that cost 100',
            'account_id': invoice_line_account,
            'invoice_line_tax_ids': [(6, 0, [tax.id])],
            'account_analytic_id': analytic_account.id,
        })

        # check that Initially supplier bill state is "Draft"
        self.assertTrue((invoice.state == 'draft'), "Initially vendor bill state is Draft")

        return invoice

    def test_01_account_invoice_create(self):
        supplier_invoice = self.create_supplier_invoice()
        price_unit = supplier_invoice.invoice_line_ids[0].price_unit
        sale_margin = 10.0
        expected_amount = (price_unit + (price_unit * (sale_margin / 100))) or 0.0
        customer = self.env.ref('base.res_partner_3')
        domain = safe_eval(
            self.env.ref('spc.action_invoice_line_tree1').read()[0]['domain'])

        # Remove from domain ('id', '>', 18873) that will be used only in production
        domain.pop(0)

        # Check lines available in 'To be Invoice to Country' List view
        tree_view_inv_lines_before = self.invoice_line_model.search(domain)

        # Check again lines available in 'To be Invoice to Country' List view
        tree_view_inv_lines_after = self.invoice_line_model.search(domain)
        self.assertEqual(tree_view_inv_lines_before, tree_view_inv_lines_after,
                         "Invoice in Draft should not be include in List View")
        supplier_invoice.action_invoice_open()

        # Ensure that a new line is now available after invoice validation
        tree_view_inv_lines_after = self.invoice_line_model.search(domain)
        new_line = tree_view_inv_lines_after - tree_view_inv_lines_before
        self.assertTrue(len(new_line) == 1,
                        "Should be available a new item in List View")

        # Create Customer invoice using 'Invoice to Country' wizard
        inv_create_wz = self.env['account.invoice.create'].with_context(
            active_ids=new_line.ids).create({
                'partner_id': self.env.ref('base.res_partner_3').id,
            })

        # Set margin to customer & re-compute amount
        customer.write({'property_sale_margin': sale_margin})
        inv_create_wz._compute_amount()

        # Review the amount
        self.assertEqual(inv_create_wz.amount, expected_amount,
                         "Unexpected amount calculation from wizard")

        view = inv_create_wz.action_invoice_create()
        customer_invoice = self.invoice_model.browse(view['res_id'])

        # Check if customer invoice has the expected amount
        self.assertEqual(customer_invoice.amount_untaxed, expected_amount,
                         "Unexpected invoice untaxed amount")

        # Check supplier invoice relationship with new invoice
        self.assertEqual(supplier_invoice.invoice_line_ids.line_dest_id,
                         customer_invoice.invoice_line_ids[0],
                         "New line should be related to the supplier invoice")
