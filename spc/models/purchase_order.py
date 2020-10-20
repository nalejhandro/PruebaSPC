from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        help="This is the sale order to associate this order's cost with."
    )

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        return res