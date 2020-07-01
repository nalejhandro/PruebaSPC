# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class Lead(models.Model):

    _inherit = 'crm.lead'

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Lead, self).message_get_suggested_recipients()
        for lead_id, data in recipients.items():
            if data:
                recipients[lead_id] = []
        return recipients


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        for partner in partner_ids:
            if partner == self.partner_id.id:
                _logger.info("Removed partner %s from sale.order %s in subscribe followers.", partner, self.id)
                partner_ids.remove(partner)
        return super(SaleOrder, self).message_subscribe(partner_ids, channel_ids, subtype_ids, force)


class SaleSubscription(models.Model):

    _inherit = 'sale.subscription'

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        for partner in partner_ids:
            if partner == self.partner_id.id:
                _logger.info("Removed partner %s from sale.subscription %s in subscribe followers.",
                             partner, self.id)
                partner_ids.remove(partner)
        return super(SaleSubscription, self).message_subscribe(partner_ids, channel_ids, subtype_ids, force)
