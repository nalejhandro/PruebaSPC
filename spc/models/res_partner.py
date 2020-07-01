# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_sale_margin = fields.Float(
        string='Sale Margin',
        company_dependent=True,
        help="This percentage will be applied to the sale price when an"
        " invoice is made to this customer using the 'Invoice to Country'"
        " wizard.")
