import logging
from odoo import models


_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):

    _inherit = 'sale.subscription'
    # The following method is brought from the module spc_sale_followers

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        for partner in partner_ids:
            if partner == self.partner_id.id:
                _logger.info("Removed partner %s from sale.subscription %s in subscribe followers.",
                             partner, self.id)
                partner_ids.remove(partner)
        return super().message_subscribe(partner_ids, channel_ids, subtype_ids, force)
