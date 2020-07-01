# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SPC Project Issue Search Attachments',
    'summary': 'Custom Issue Search in attachments by name, description'
               ' or indexed text',
    'version': '8.0.1.0',
    'category': 'Project Management',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': ['project_issue', 'document'],
    'data': ['views/project_issue_search_attachments_view.xml']
}
