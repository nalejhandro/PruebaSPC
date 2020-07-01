# -*- coding: utf-8 -*-
import json
import requests

from odoo import api, models
from odoo.addons.google_account.models.google_service import TIMEOUT
from odoo.tools.translate import _


class GoogleDrive(models.Model):
    _inherit = 'google.drive.config'

    @api.model
    def copy_doc(self, res_id, template_id, name_gdocs, res_model):
        # Remove the standard permission which the google_drive app creates.
        res = super(GoogleDrive, self).copy_doc(res_id, template_id, name_gdocs, res_model)
        if not res:
            return res
        access_token = self.get_access_token()
        key = self._get_key_from_url(res['url'])
        request_url = "https://www.googleapis.com/drive/v2/files/%s/permissions/anyoneWithLink?access_token=%s" % (
            key, access_token)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        data = {}
        try:
            req = requests.delete(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
        except requests.HTTPError:
            raise self.env['res.config.settings'].get_config_warning(
                _("The permission 'reader' for 'anyone with the link' has not been removed on the document"))
        return res
