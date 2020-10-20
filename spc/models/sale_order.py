from odoo import models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        if res.opportunity_id:
            res.name = res.name + '-' + str(res.opportunity_id.id)
        return res
