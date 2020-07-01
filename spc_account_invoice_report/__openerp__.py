# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Spc Account Invoice Report',
    'summary': 'Spc Account Invoice Report',
    'version': '8.0.1.0',
    'category': 'accountant',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'base',
        'account',
        'account_invoice_report',
        'l10n_hn_company',
        'spc_account_invoice_line',
    ],
    'data': [
        'data/report.paperformat.xml',
        'data/spc_report_invoice.xml',
        'views/spc_account_invoice_report.xml',
    ],
}
