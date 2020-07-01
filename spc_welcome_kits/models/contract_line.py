# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ContractLine(models.Model):

    _name = "sale.order.contract.line"

    # New fields for welcome kits
    order_id = fields.Many2one("sale.order", "Sale Order")
    contract = fields.Char('Contract')
    service_level = fields.Char('Service Level')
    site_name = fields.Char('Site Name')
    product_number = fields.Char('Product Number')
    serial_number = fields.Char('Equipment Serial Number')
    begin_date = fields.Date('Begin Date')
    end_date = fields.Date('End Date')
