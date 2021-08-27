import logging
from odoo import fields, models, api


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    date_commitment = fields.Date(related='opportunity_id.date_commitment', readonly=True, store=True)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super().create(vals)
        # Forces the external ID creation as well
        res._BaseModel__ensure_xml_id()
        if res.opportunity_id:
            res.name = "%s-%s" % (res.name, res.opportunity_id.id)
        return res

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        """The following method is brought from the module spc_sale_followers"""
        for partner in partner_ids:
            if partner == self.partner_id.id:
                _logger.info("Removed partner %s from sale.order %s in subscribe followers.", partner, self.id)
                partner_ids.remove(partner)
        return super().message_subscribe(partner_ids, channel_ids, subtype_ids)
