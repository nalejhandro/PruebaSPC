# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    date_delivery_equipment = fields.Date('Equipment Delivery Date')
    date_delivery_service = fields.Date('Service Delivery Date')
    date_invoicing = fields.Date('Estimated Invoicing Date')
