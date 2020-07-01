# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'l10n_hn_company',
    'summary': 'Add attributes to company HON',
    'version': '8.0.1.0',
    'category': 'Reports',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'base',
    ],
    'data': [
        'views/res_company_view.xml',
    ],
}
