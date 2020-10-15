from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestStockMove(TransactionCase):
    """Test cases for stock.move model"""

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_delivery_01')
        self.input = 'ABC012,DEF345,GHI678'

    def create_purchase(self, line=None):
        """Helper function to create a purchase order."""
        line = line or {}
        line_values = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_qty': 3.0,
            'product_uom': self.product.uom_po_id.id,
            'price_unit': 300,
            'date_planned': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        }
        line_values.update(line)
        order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, line_values)],
        })
        return order

    def test_01_serial_tracking_set_serial_number(self):
        """Validates that the serial numbers are correctly assigned when the
        product tracking is set to 'By Unique Serial Number'."""
        self.product.write({'tracking': 'serial'})
        purchase_order = self.create_purchase()
        purchase_order.button_confirm()

        self.assertEqual(
            purchase_order.picking_count, 1, "One picking should be created.")

        picking = purchase_order.picking_ids[0]
        move = picking.move_lines[0]

        self.assertEqual(
            len(move.move_line_ids), 3, "Three move lines should be created.")

        # Try to assign serial numbers without providing an input string
        error_msg = "To use this feature, you must provide a valid*."
        with self.assertRaisesRegexp(ValidationError, error_msg):
            move.set_unique_serial_number()

        # Try to assign serial numbers with an invalid input string
        move.write({'serial_numbers': 'ABC012   DEF345'})
        with self.assertRaisesRegexp(ValidationError, error_msg):
            move.set_unique_serial_number()

        # Try to assign the serial numbers with less information
        # than necessary
        move.write({'serial_numbers': 'ABC012,DEF345'})
        error_msg = "There is no correspondence between*."
        with self.assertRaisesRegexp(ValidationError, error_msg):
            move.set_unique_serial_number()

        # Try to assign the serial numbers with more information
        # than necessary
        move.write({'serial_numbers': 'ABC012,DEF345,GHI678,XYZ901'})
        with self.assertRaisesRegexp(ValidationError, error_msg):
            move.set_unique_serial_number()

        move.write({'serial_numbers': self.input})
        move.set_unique_serial_number()

        # Checks if the result obtained after assigning the serial numbers
        # automatically is as expected.
        self.assertEqual(
            ','.join(move.move_line_ids.mapped('lot_name')), self.input,
            "The serial numbers were not assigned incorrectly."
        )

        self.assertEqual(
            sum(move.move_line_ids.mapped('qty_done')), 3.0,
            "The value for done quantity is wrong."
        )

    def test_02_lot_tracking_set_serial_number(self):
        """Validates that the serial numbers are correctly assigned when the
        product tracking is set to 'By Lots'."""
        self.product.write({'tracking': 'lot'})
        purchase_order = self.create_purchase()
        purchase_order.button_confirm()

        self.assertEqual(
            purchase_order.picking_count, 1, "One picking should be created.")

        picking = purchase_order.picking_ids[0]
        move = picking.move_lines[0]

        self.assertEqual(
            len(move.move_line_ids), 1, "One move line should be created.")

        move.write({'serial_numbers': self.input})
        move.set_unique_serial_number()

        # Checks if the result obtained after assigning the serial numbers
        # automatically is as expected.
        self.assertEqual(
            len(move.move_line_ids), 3, "Three move lines should be created.")

        self.assertEqual(
            ','.join(move.move_line_ids.mapped('lot_name')), self.input,
            "The serial numbers were not assigned incorrectly."
        )

        self.assertEqual(
            sum(move.move_line_ids.mapped('qty_done')), 3.0,
            "The value for done quantity is wrong."
        )
