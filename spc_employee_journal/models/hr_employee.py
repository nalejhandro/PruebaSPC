# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    journal_id = fields.Many2one(
        'account.analytic.journal', string='Analytic Journal',
        company_dependent=True)
