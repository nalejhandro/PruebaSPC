import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)
try:
    from oauth2client.client import OAuth2WebServerFlow
except (ImportError, IOError) as err:
    _logger.debug(err)

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_ID = '149905831071-d08bancbk563mj8avccqnfpc12rllimv.apps.googleusercontent.com'
CLIENT_SECRET = '8KXLgti93Qn990cnspaZ_0Cp'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

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

    bc_template = fields.Many2one(
        'google.drive.config', string='BC Template')
    bc_authorization_code = fields.Char(
        'BC Sync Authorization Code')
    bc_uri = fields.Char(
        'BC Sync URI', compute='_compute_bc_uri')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        template_str = icpsudo.get_param('spc_crm.bc_template')
        res.update(
            bc_template=template_str and int(template_str) or False,
            bc_authorization_code=icpsudo.get_param('spc_crm.bc_authorization_code'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        icpsudo.set_param('spc_crm.bc_template', str(self.bc_template.id))
        if self.bc_authorization_code and \
                self.bc_authorization_code != icpsudo.get_param('spc_crm.bc_authorization_code'):
            icpsudo.set_param("spc_crm.bc_authorization_code", self.bc_authorization_code)
            flow = OAuth2WebServerFlow(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                scope=SCOPES,
                redirect_uri=REDIRECT_URI)
            credentials = flow.step2_exchange(self.bc_authorization_code)
            icpsudo.set_param('spc_crm.bc_credentials', credentials.to_json())
        return True
