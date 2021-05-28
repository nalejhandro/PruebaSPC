from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request


class CustomerPortalIntrUsers(CustomerPortal):

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        res = super().portal_my_quotes(page=1, date_begin=None, date_end=None, sortby=None, **kw)
        if not request.env.user.has_group('base.group_user'):
            return request.redirect("/my/quotes")
        return res

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        res = super().portal_order_page(
            order_id, report_type=None, access_token=None, message=False, download=False, **kw)
        if not request.env.user.has_group('base.group_user'):
            return request.redirect("/my/orders")
        return res
