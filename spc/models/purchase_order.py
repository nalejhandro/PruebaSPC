from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        help="This is the sale order to associate this order's cost with."
    )
