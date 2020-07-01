from odoo import models, api

class ProcurementComputeAll(models.TransientModel):

    _inherit = 'procurement.order.compute.all'

    @api.multi
    def procure_calculation(self):
        return super(ProcurementComputeAll, self).sudo().procure_calculation()
