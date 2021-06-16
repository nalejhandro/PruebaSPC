from odoo import fields, models


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    def _get_default_check(self):
        model = self.env.context.get('default_res_model')
        return model not in ['crm.lead', 'sale.order', 'account.move']

    send_mail = fields.Boolean(
        default=_get_default_check,
    )
