# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SPC Sale Costs',
    'summary': 'Costs for SPC Sales',
    'version': '13.0.0.1.0',
    'category': 'Sales Management',
    'author': 'ClearCorp, Vauxoo',
    'license': 'AGPL-3',
    'sequence': 20,
    'depends': [
        'sale_stock',
        'stock_account_move_line',
    ],
    'data': [
        'security/spc_sale_costs_security.xml',
        'views/picking_type_view.xml',
        'views/account_view.xml',
        'views/sale_order_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
