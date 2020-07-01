# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields


class Move(models.Model):

    _inherit = 'account.move'

    manual_move = fields.Boolean('Manual', default=False, readonly=True, help='Entries created manually')
