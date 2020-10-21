{
    'name': 'SPC Internacional App',
    'version': '13.0.1.0.3',
    "author": "Vauxoo",
    "license": "LGPL-3",
    'category': 'Installer',
    'summary': 'SPC Internacional App for customizations',
    'depends': [
        'account_accountant',
        'account_budget',
        'attachment_indexation',
        'auth_oauth',
        'board',
        'sale_crm',
        'google_spreadsheet',
        'helpdesk_timesheet',
        'hr_payroll',
        'im_livechat',
        'inter_company_rules',
        'l10n_cr',
        'ocn_client',
        'purchase_requisition',
        'sale_product_configurator',
        'sale_subscription',
        'stock_dropshipping',
        'stock_landed_costs',
        'survey',
        'website_forum',
        'website_helpdesk',
        'product_brand',
        'project_task_default_stage',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'security/spc_security.xml',
        'views/stock_move_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'views/crm_lead_view.xml',
        'views/res_config_settings_views.xml',
        'views/spc_crm_lead_manufacturer.xml',
        'wizards/account_invoice_create_views.xml',
    ],
    'external_dependencies': {
        'python': [
            'oauth2client.client',
        ],
    },
    'demo': [
        'demo/res_partner_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'pre_init_hook': 'pre_init_hook',
}
