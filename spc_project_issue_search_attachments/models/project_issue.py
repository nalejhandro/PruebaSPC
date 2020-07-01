# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class ProjectIssue(models.Model):
    _inherit = "project.issue"

    @api.model
    def _search_related_attachments(self, operator, value):
        if operator == 'like':
            operator = 'ilike'
        attachments = self.env["ir.attachment"].search(
                ['|', ('name', operator, value), '|',
                 ('description',  operator, value),
                 ('index_content', operator, value),
                 ('res_model', '=', self._name)])
        issue_ids = [attachment.res_id for attachment in attachments]
        return [('id', 'in', issue_ids)]

    @api.multi
    def _compute_related_attachments(self):
        for issue in self:
            issue.attachment_ids = self.env["ir.attachment"].search(
                 [('res_model', '=', self._name),
                  ('res_id', '=', issue.id)])

    attachment_ids = fields.One2many('ir.attachment',
                                     string='Related Attachments',
                                     compute='_compute_related_attachments',
                                     search='_search_related_attachments')
