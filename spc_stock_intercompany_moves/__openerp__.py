# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'SPC Intercompany Stock Moves',
    'version': '1.0',
    'category': 'Warehouse',
    'sequence': 5,
    'summary': 'Transfers with transit locations',
    'description': """
Features
--------
* Allows the user to reserve quants from transit locations.
* Disables to force availability in transit locations.
* Enables to force availability just directly from pickings.""",
    'author': 'ClearCorp',
    'depends': ['stock_account'],
    'data': ['stock_intercompany_moves_view.xml'],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
