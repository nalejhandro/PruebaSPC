from openerp import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    # New fields for welcome kits
    wk_long_service_level = fields.Char('Service Level Link')
    contract_line_ids = fields.One2many(
        "sale.order.contract.line", "order_id", string="Welcome-Kit Lines")