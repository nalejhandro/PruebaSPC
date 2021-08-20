from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_compute_recipients(self, message, msg_vals):
        res = super()._notify_compute_recipients(message, msg_vals)
        is_model = msg_vals.get('model') in ['sale.order', 'account.move', 'crm.lead']
        if res.get('partners') and is_model:
            mail_domain = self.env.ref('spc.email_domain_restricted_messages')
            partners = [partner['id'] for partner in res['partners']]
            internal = self.env.ref('base.group_user')
            users = self.env['res.users'].search_read(
                [('partner_id', 'in', partners), ('groups_id', 'in', internal.ids)],
                ['partner_id', 'login'],
            )
            partner_ids = [user['partner_id'][0] for user in users if
                           user['login'].split('@')[1] in mail_domain.value.split(',')]
            recipients = []
            for index, partner in enumerate(res['partners']):
                if partner['id'] in partner_ids:
                    recipients.append(res['partners'][index])
            res['partners'] = recipients
        return res
