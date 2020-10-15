from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    line_dest_id = fields.Many2one(
        'account.move.line',
        string='Downstream Line',
        readonly=True,
        help="If it's filled, it's because a customer invoice line was generated"
        " from this line."
    )
    invoice_dest_id = fields.Many2one(
        'account.move',
        related='line_dest_id.move_id',
        string='Downstream Invoice',
        help="If it's filled, it's because a customer invoice line was generated"
        " from this line."
    )
