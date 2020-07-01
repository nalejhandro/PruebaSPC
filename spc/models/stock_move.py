# -*- coding: utf-8 -*-
import re
from odoo import exceptions, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    serial_numbers = fields.Char(
        help="A string that contains several unique serial numbers separated"
        " by commas."
    )

    def set_unique_serial_number(self):
        """Assigns a serial number to each move line based on the input string
        provided by the user."""
        if not self.serial_numbers or ',' not in self.serial_numbers:
            raise exceptions.ValidationError(
                _("To use this feature, you must provide a valid input string."
                  " E.g. ABC012,DEF345,XYZ678")
            )

        numbers = [
            number for number in re.sub(
                ' ', '', self.serial_numbers).split(',') if number]

        # Most products in the system have the tracking set to 'By Lots' even
        # when they need to be treated as 'By Unique Serial Number'.
        # Due to this, we need a way to split a stock.move.line depending on
        # the initial demand. So a stock.move.line associated with an initial
        # demand of three will be converted into three stock.move.line.
        if len(self.move_line_ids) == 1 and\
                len(numbers) == self.product_uom_qty:
            while len(self.move_line_ids) < self.product_uom_qty:
                self.move_line_ids[0].copy()
            self.move_line_ids.write({'product_uom_qty': 1})

        if len(numbers) != len(self.move_line_ids):
            raise exceptions.ValidationError(
                _("There is no correspondence between the number of serials to"
                  " assign (%d) and the number of lines in the movement (%d).")
                % (len(numbers), len(self.move_line_ids))
            )

        for index, line in enumerate(self.move_line_ids):
            line.write({
                'lot_name': numbers[index],
                'qty_done': line.product_uom_qty,
            })
