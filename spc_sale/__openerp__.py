# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SPC Custom Sale',
    'summary': 'Adds custom behavior for sale',
    'version': '8.0.1.0',
    'category': 'Sales',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 16,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
}
