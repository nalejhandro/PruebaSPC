# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _

import werkzeug.urls
import urllib2
import json
import re
import openerp

_logger = logging.getLogger(__name__)

class SPCGoogleDrive(osv.Model):
    
     _inherit = "google.drive.config"
     
     def copy_doc(self, cr, uid, res_id, template_id, name_gdocs, res_model, context=None):
        ir_config = self.pool['ir.config_parameter']
        google_web_base_url = ir_config.get_param(cr, SUPERUSER_ID, 'web.base.url')
        access_token = self.get_access_token(cr, uid, context=context)
        # Copy template in to drive with help of new access token
        request_url = "https://www.googleapis.com/drive/v2/files/%s?fields=parents/id&access_token=%s" % (template_id, access_token)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept-Encoding": "deflate"}
        try:
            req = urllib2.Request(request_url, None, headers)
            parents = urllib2.urlopen(req).read()
        except urllib2.HTTPError:
            raise osv.except_osv(_('Warning!'), _("The Google Template cannot be found. Maybe it has been deleted."))
        parents_dict = json.loads(parents)

        record_url = "Click on link to open Record in Odoo\n %s/?db=%s#id=%s&model=%s" % (google_web_base_url, cr.dbname, res_id, res_model)
        data = {"title": name_gdocs, "description": record_url, "parents": parents_dict['parents']}
        request_url = "https://www.googleapis.com/drive/v2/files/%s/copy?access_token=%s" % (template_id, access_token)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data_json = json.dumps(data)
        # resp, content = Http().request(request_url, "POST", data_json, headers)
        req = urllib2.Request(request_url, data_json, headers)
        content = urllib2.urlopen(req).read()
        content = json.loads(content)
        res = {}
        if content.get('alternateLink'):
            attach_pool = self.pool.get("ir.attachment")
            attach_vals = {'res_model': res_model, 'name': name_gdocs, 'res_id': res_id, 'type': 'url', 'url': content['alternateLink']}
            res['id'] = attach_pool.create(cr, uid, attach_vals)
            # Commit in order to attach the document to the current object instance, even if the permissions has not been written.
            cr.commit()
            res['url'] = content['alternateLink']
            key = self._get_key_from_url(res['url'])
            request_url = "https://www.googleapis.com/drive/v2/files/%s/permissions?emailMessage=This+is+a+drive+file+created+by+Odoo&sendNotificationEmails=false&access_token=%s" % (key, access_token)
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)# select the active user 
            data = {'role': 'writer', 'type': 'user', 'withLink': False, 'value': user.email}#add the permissions for the google doc
            try:
                req = urllib2.Request(request_url, json.dumps(data), headers)
                urllib2.urlopen(req)
            except urllib2.HTTPError:
                raise self.pool.get('res.config.settings').get_config_warning(cr, _("The permission 'reader' for 'anyone with the link' has not been written on the document"), context=context)
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if user.email:
                data = {'role': 'writer', 'type': 'user', 'value': user.email}
                try:
                    req = urllib2.Request(request_url, json.dumps(data), headers)
                    urllib2.urlopen(req)
                except urllib2.HTTPError:
                    pass
        return res 
