# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'SPC Internacional App',
    'version': '11.0.0.0.3',
    "author": "Vauxoo",
    "license": "AGPL-3",
    'category': 'Installer',
    'summary': 'SPC Internacional App for customizations',
    'depends': [
        # Accounting
        'account_accountant',

        # Stock
        'stock',

        # Purchase
        'purchase',

        # Sale
        'sale_management',

    ],
    'data': [
        'views/stock_move_views.xml',
        'security/res_groups.xml',
        'views/account_invoice_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'wizard/account_invoice_create_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
