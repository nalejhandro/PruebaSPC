from odoo import models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # The following method is brought from the module spc_analytic
    _sql_constraints = [
        ('unique_name_company', 'UNIQUE(name, company_id)',
         'Account/Contract Name must be unique per company.'),
    ]
