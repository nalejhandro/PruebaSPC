# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SPC Welcome Kits',
    'summary': 'Custom reports for partner welcome kits',
    'version': '8.0.1.0',
    'category': 'Sales Management',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'sale', 'partner_trade_name', 'report_aeroo'
    ],
    'data': [
        'report/welcome_kits_report.xml',
        'report/advanced_replacement_services_template.xml',
        'views/sale_order_view.xml',
        'views/sale_order_line_view.xml',
        'views/account_analytic_account_view.xml',
        'views/stock_production_lot_view.xml',
        'security/ir.model.access.csv'
    ]
}
