from datetime import datetime
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _order = 'id ASC'

    date_stage_change = fields.Datetime(
        'Date of last stage update',
        readonly=True
    )

    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_stage_change'] = datetime.now()
        return super(CrmLead, self).write(vals)

    def _get_selection_values(self):
        companies = self.env.user.company_ids
        return [(company.id, company.name) for company in companies]

    @api.depends('company_id')
    def _compute_change_company_id(self):
        for lead in self:
            lead.change_company_id = False

    def _inverse_change_company_id(self):
        for lead in self:
            lead.company_id = lead.change_company_id

    change_company_id = fields.Selection(
        selection=_get_selection_values,
        string='Change Company', compute='_compute_change_company_id',
        inverse='_inverse_change_company_id',
        help='Use this field to change this opportunity between companies.')
    client_requirement = fields.Text()
    project_scope = fields.Text()
    success_factors = fields.Text('Critical Factors of Success')
    items_out_of_reach = fields.Text('Items Out of Reach')
    observation = fields.Text('Observations')
    detail_incidentals = fields.Float(
        'Incidentals', digits=dp.get_precision('Account'))
    detail_total_revenue = fields.Float(
        'Total Revenue', digits=dp.get_precision('Account'))
    detail_product_cost = fields.Float(
        'Product Cost', digits=dp.get_precision('Account'))
    detail_product_price = fields.Float(
        'Product Price', digits=dp.get_precision('Account'))
    detail_product_price_vat = fields.Float(
        'Product Price + VAT', digits=dp.get_precision('Account'))
    detail_product_profit = fields.Float(
        'Product Profit', digits=dp.get_precision('Account'))
    detail_product_markup = fields.Float(
        'Product Markup', digits=dp.get_precision('Account'))
    detail_warranty_cost = fields.Float(
        'Warranty Cost', digits=dp.get_precision('Account'))
    detail_warranty_price = fields.Float(
        'Warranty Price', digits=dp.get_precision('Account'))
    detail_warranty_price_vat = fields.Float(
        'Warranty Price + VAT', digits=dp.get_precision('Account'))
    detail_warranty_profit = fields.Float(
        'Warranty Profit', digits=dp.get_precision('Account'))
    detail_warranty_markup = fields.Float(
        'Warranty Markup', digits=dp.get_precision('Account'))
    detail_service_cost = fields.Float(
        'Service Cost', digits=dp.get_precision('Account'))
    detail_service_price = fields.Float(
        'Service Price', digits=dp.get_precision('Account'))
    detail_service_price_vat = fields.Float(
        'Service Price + VAT', digits=dp.get_precision('Account'))
    detail_service_profit = fields.Float(
        'Service Profit', digits=dp.get_precision('Account'))
    detail_service_markup = fields.Float(
        'Service Markup', digits=dp.get_precision('Account'))
    detail_material_cost = fields.Float(
        'Material Cost', digits=dp.get_precision('Account'))
    detail_material_price = fields.Float(
        'Material Price', digits=dp.get_precision('Account'))
    detail_material_price_vat = fields.Float(
        'Material Price + VAT', digits=dp.get_precision('Account'))
    detail_material_profit = fields.Float(
        'Material Profit', digits=dp.get_precision('Account'))
    detail_material_markup = fields.Float(
        'Material Markup', digits=dp.get_precision('Account'))
    detail_service_expense_cost = fields.Float(
        'Service Expense Cost', digits=dp.get_precision('Account'))
    detail_service_expense_price = fields.Float(
        'Service Expense Price', digits=dp.get_precision('Account'))
    detail_service_expense_price_vat = fields.Float(
        'Service Expense Price + VAT', digits=dp.get_precision('Account'))
    detail_service_expense_profit = fields.Float(
        'Service Expense Profit', digits=dp.get_precision('Account'))
    detail_service_expense_markup = fields.Float(
        'Service Expense Markup', digits=dp.get_precision('Account'))
    detail_total_cost = fields.Float(
        'Total Cost', digits=dp.get_precision('Account'))
    detail_total_price = fields.Float(
        'Total Price', digits=dp.get_precision('Account'))
    detail_total_price_vat = fields.Float(
        'Total Price + VAT', digits=dp.get_precision('Account'))
    detail_total_profit = fields.Float(
        'Total Profit', digits=dp.get_precision('Account'))
    detail_total_markup = fields.Float(
        'Total Markup', digits=dp.get_precision('Account'))
