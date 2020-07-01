# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    main_unit = fields.Selection([
        ('cibersecurity', 'CyberSecurity'), ('datacenter', 'DataCenter'),
        ('it_services', 'IT Services'), ('networking', 'Networking')],
        string='Principal Address', oldname='principal_address')
    manufacturer_line_ids = fields.One2many(
        'spc.crm.lead.manufacturer.line', 'lead_id', string='Manufacturer')


class CRMManufacturerLine(models.Model):
    _name = 'spc.crm.lead.manufacturer.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    product_brand_id = fields.Many2one('product.brand', string='Manufacturer')
    code = fields.Char()
    estimate = fields.Float(string='Estimate %')


class ProductBrand(models.Model):
    _inherit = 'product.brand'

    manufacturer_line_ids = fields.One2many(
        'spc.crm.lead.manufacturer.line', 'product_brand_id',
        string='Manufacturer')
