# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import re
# import httplib2
# from apiclient import discovery
# from odoo.exceptions import Warning
import logging
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

# from oauth2client.client import Credentials

# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
# CLIENT_ID = '149905831071-d08bancbk563mj8avccqnfpc12rllimv.apps.googleusercontent.com'
# CLIENT_SECRET = '8KXLgti93Qn990cnspaZ_0Cp'
# REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

_logger = logging.getLogger(__name__)


class Lead(models.Model):

    _inherit = 'crm.lead'
    _order = 'id ASC'

    # @api.one
    # def get_credentials(self):
    #     ir_config = self.env['ir.config_parameter']
    #     credentials_json = ir_config.sudo().get_param(
    #         'spc_crm_bc_credentials')
    #     if credentials_json:
    #         credentials = Credentials.new_from_json(credentials_json)
    #     else:
    #         credentials = None
    #     if not credentials or credentials.invalid:
    #         raise Warning(_(
    #             'Google Drive is not yet configured. Please contact '
    #             'your administrator.'))
    #     return credentials
    #
    # @api.one
    # def set_credentials(self, credentials):
    #     ir_config = self.env['ir.config_parameter']
    #     if credentials:
    #         ir_config.sudo().set_param(
    #             'spc_crm_bc_credentials', credentials.to_json(),
    #             groups=['base.group_system'])
    #         _logger.info('Storing new credentials')
    #         return True
    #     return False
    #
    # @api.one
    # def read_data_from_business_case(self, attachment):
    #     credentials = self.get_credentials()[0]
    #     store_credentials = False
    #     if credentials. access_token_expired:
    #         store_credentials = True
    #     http = credentials.authorize(httplib2.Http())
    #     discoveryUrl = (
    #         'https://sheets.googleapis.com/$discovery/rest?version=v4')
    #     service = discovery.build(
    #         'sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    #
    #     regex = re.compile('\/d\/(.*)\/')
    #     res = regex.search(attachment.url)
    #     spreadsheet_id = res.group(1)
    #     range_name = 'Resultados!C17:G22'
    #
    #     #Read Details
    #     result = service.spreadsheets().values().get(
    #         spreadsheetId=spreadsheet_id, range=range_name,
    #         valueRenderOption='UNFORMATTED_VALUE').execute()
    #     values = result.get('values', [])
    #     if store_credentials:
    #         self.set_credentials(credentials)
    #     res = {
    #         'detail_product_cost': float(values[0][0]),
    #         'detail_product_price': float(values[0][1]),
    #         'detail_product_price_vat': float(values[0][2]),
    #         'detail_product_profit': float(values[0][3]),
    #         'detail_product_markup': float(values[0][4]),
    #         'detail_warranty_cost': float(values[1][0]),
    #         'detail_warranty_price': float(values[1][1]),
    #         'detail_warranty_price_vat': float(values[1][2]),
    #         'detail_warranty_profit': float(values[1][3]),
    #         'detail_warranty_markup': float(values[1][4]),
    #         'detail_service_cost': float(values[2][0]),
    #         'detail_service_price': float(values[2][1]),
    #         'detail_service_price_vat': float(values[2][2]),
    #         'detail_service_profit': float(values[2][3]),
    #         'detail_service_markup': float(values[2][4]),
    #         'detail_material_cost': float(values[3][0]),
    #         'detail_material_price': float(values[3][1]),
    #         'detail_material_price_vat': float(values[3][2]),
    #         'detail_material_profit': float(values[3][3]),
    #         'detail_material_markup': float(values[3][4]),
    #         'detail_service_expense_cost': float(values[4][0]),
    #         'detail_service_expense_price': float(values[4][1]),
    #         'detail_service_expense_price_vat': float(values[4][2]),
    #         'detail_service_expense_profit': float(values[4][3]),
    #         'detail_service_expense_markup': float(values[4][4]),
    #         'detail_total_cost': float(values[5][0]),
    #         'detail_total_price': float(values[5][1]),
    #         'detail_total_price_vat': float(values[5][2]),
    #         'detail_total_profit': float(values[5][3]),
    #         'detail_total_markup': float(values[5][4]),
    #     }
    #
    #     # Read Margins
    #     range_name = 'Resultados!C14:G14'
    #     result = service.spreadsheets().values().get(
    #         spreadsheetId=spreadsheet_id, range=range_name,
    #         valueRenderOption='UNFORMATTED_VALUE').execute()
    #     values = result.get('values', [])
    #     res.update({
    #         'x_planned_contribution_margin': float(values[0][0]),
    #         'detail_incidentals': float(values[0][2]),
    #         'detail_total_revenue': float(values[0][4]),
    #     })
    #     return res
    #
    # @api.multi
    # def sync_business_case(self):
    #     for lead in self:
    #         # Verify if this lead has an attachment
    #         config_param = self.env['ir.config_parameter']
    #         tempate_str = config_param.get_param('spc_crm_bc_template')
    #         config_id = tempate_str and int(tempate_str) or False
    #         if not config_id:
    #             raise Warning(_(
    #                 'The sync template is not configured. Please ask the'
    #                 ' Administrator to set it up.'))
    #         config = self.env['google.drive.config'].sudo().browse(config_id)
    #         model = config.model_id
    #         filter_name = config.filter_id and config.filter_id.name or False
    #         record = self.read([])[0]
    #         record.update({'model': model.name, 'filter': filter_name})
    #         name_gdocs = config.name_template
    #         try:
    #             name_gdocs = name_gdocs % record
    #         except:
    #             raise Warning(_(
    #                 'At least one key cannot be found in your Google Drive'
    #                 ' name pattern'))
    #         attachment = self.env['ir.attachment'].search([
    #             ('res_model', '=', model.model),
    #             ('name', '=', name_gdocs),
    #             ('res_id', '=', lead.id)], limit=1)
    #         if attachment:
    #             # Catch exceptions for invalid data
    #             try:
    #                 data = lead.read_data_from_business_case(attachment)[0]
    #                 lead.write(data)
    #             except Exception:
    #                 _logger.info('Unable to sync for this BC version.')
    #     return True
    #
    # def sync_business_case_all(self, stage_ids=[]):
    #     """Sync all bussiness_case in the states specified"""
    #     leads = self.search([('stage_id', 'in', stage_ids)])
    #     for lead in leads:
    #         try:
    #             lead.sync_business_case()
    #         except:
    #             _logger.error('Error processing lead %s.' % lead.id)
    #     return True

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
