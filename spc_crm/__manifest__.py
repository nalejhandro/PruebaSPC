# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SPC Custom CRM',
    'summary': 'Custom extensions for SPC CRM',
    'version': '11.0.0.1.0',
    'category': 'Customer Relationship Management',
    'author': 'ClearCorp, Vauxoo',
    'license': 'AGPL-3',
    'sequence': 3,
    'depends': [
        'crm',
        'sale_crm',
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/sale_config_settings_view.xml',
        'data/spc_crm_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'oauth2client.client',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
