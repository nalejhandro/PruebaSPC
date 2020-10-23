import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)

try:
    from oauth2client.client import OAuth2WebServerFlow
except (ImportError, IOError) as err:
    _logger.debug(err)

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_ID = '149905831071-d08bancbk563mj8avccqnfpc12rllimv.apps.googleusercontent.com'
CLIENT_SECRET = '8KXLgti93Qn990cnspaZ_0Cp'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


class ResCompany(models.Model):
    _inherit = 'res.company'

    bc_template = fields.Many2one('google.drive.config', string='BC Template')
    bc_authorization_code = fields.Char('BC Sync Authorization Code')
    bc_uri = fields.Char('BC Sync URI', compute='_compute_bc_uri')
    prefix = fields.Char('Prefix', size=10, default='')

    def name_get(self):
        res = dict(super(ResCompany, self).name_get())
        for company in self.browse(res.keys()):
            company_name = "%s " % company.prefix if company.prefix else ''
            company_name += company.name
            res[company.id] = company_name
        return list(res.items())

    @api.depends('bc_authorization_code')
    def _compute_bc_uri(self):
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPES,
            redirect_uri=REDIRECT_URI)
        auth_uri = flow.step1_get_authorize_url()
        for config in self:
            config.bc_uri = auth_uri


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    bc_template = fields.Many2one(
        'google.drive.config', string='BC Template',
        related="company_id.bc_template", readonly=False)
    bc_authorization_code = fields.Char(
        'BC Sync Authorization Code',
        related="company_id.bc_authorization_code", readonly=False)
    bc_uri = fields.Char('BC Sync URI', compute='_compute_bc_uri', related="company_id.bc_uri")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.company_id
        res.update(
            bc_template=company.bc_template,
            bc_authorization_code=company.bc_authorization_code,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        if self.bc_authorization_code:
            flow = OAuth2WebServerFlow(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                scope=SCOPES,
                redirect_uri=REDIRECT_URI)
            credentials = flow.step2_exchange(self.bc_authorization_code)
            icpsudo.set_param('spc.bc_credentials', credentials.to_json())
        return True
