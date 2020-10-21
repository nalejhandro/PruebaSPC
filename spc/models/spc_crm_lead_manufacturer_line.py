from odoo import fields, models


class CRMManufacturerLine(models.Model):
    _name = 'spc.crm.lead.manufacturer.line'
    _description = "Lead Manufacture Line"

    lead_id = fields.Many2one('crm.lead')
    product_brand_id = fields.Many2one('product.brand', string='Manufacturer')
    code = fields.Char()
    estimate = fields.Float(string='Estimate %')
