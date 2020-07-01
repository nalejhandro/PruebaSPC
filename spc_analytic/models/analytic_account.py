# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    _sql_constraints = [
        ('unique_name_company', 'UNIQUE(name, company_id)',
         'Account/Contract Name must be unique per company.'),
    ]
