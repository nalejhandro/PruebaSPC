#!/usr/bin/env python
#-*- encoding: utf8 -*-

import os
import sys
import glob
import argparse
from textwrap import dedent
import traceback

import psycopg2

MODELS_TO_DELETE = (
  'ir.actions.act_window',
  'ir.actions.act_window.view',
  'ir.actions.report.xml',
  'ir.actions.todo',
  'ir.actions.url',
  'ir.actions.wizard',
  'ir.cron',
  'ir.model',
  'ir.model.access',
  'ir.model.fields',
  'ir.module.repository',
  'ir.property',
  'ir.report.custom',
  'ir.report.custom.fields',
  'ir.rule',
  'ir.sequence',
  'ir.sequence.type',
  'ir.ui.menu',
  'ir.ui.view',
  'ir.ui.view_sc',
  'ir.values',
  'res.groups',
)

DEPRECATED_MODELS = {
    '13.0': (
        'ir.qweb.widget', 'ir.qweb.widget.monetary',
        'pos.confirm', 'pos.details', 'stock.move.scrap',
        'report.transaction.pos',
        'report.sales.by.user.pos',
        'report.sales.by.user.pos.month',
        'report.point_of_sale.report_payment',
        'report.point_of_sale.report_statement',
        'report.point_of_sale.report_receipt',
        'report.point_of_sale.report_saleslines',
        'report.point_of_sale.report_detailsofsales'
    ),
}

# Hacked by Vauxoo -:
# Just added our modules tested that will be able to mantain installed
# after the upgrade.
OUR_MODULES = {
    '13.0': """
    crm_sms web_grid sale_subscription_dashboard website_helpdesk_livechat
    web_enterprise hr_holidays_gantt helpdesk_sale_timesheet web_gantt
    web_mobile website_helpdesk_forum ocn_client website_helpdesk
    website_enterprise helpdesk_timesheet inter_company_rules web_kanban_gauge
    auth_signup attachment_indexation auth_oauth web_diagram contacts
    website_partner gamification_sale_crm calendar_sms payment_transfer rating
    google_spreadsheet hr_contract stock_dropshipping google_account barcodes
    google_drive stock_landed_costs board account_predictive_bills mail_bot
    snailmail web_unsplash account_facturx im_livechat_mail_bot
    project_enterprise website_theme_install partner_autocomplete
    account_invoice_extract project_timesheet_holidays
    project_timesheet_synchro website_rating crm_enterprise sale_enterprise
    snailmail_account_followup stock_account_enterprise stock stock_enterprise
    hr_payroll_account web_cohort base_automation base_automation_hr_contract
    crm_livechat website_mail sale_product_configurator
    account account_accountant stock_sms timesheet_grid sale_timesheet_purchase
    website_sms crm website_forum hr_holidays_calendar sale_purchase
    im_livechat_enterprise utm website_profile web_tour web_map web_dashboard
    helpdesk_sale purchase_requisition_stock analytic_enterprise survey
    snailmail_account account_budget purchase_stock base
    sale_timesheet_enterprise base_import hr_gamification purchase_requisition
    hr_contract_reports purchase_enterprise purchase hr_timesheet
    account_auto_transfer sales_team stock_account hr_work_entry
    website_crm_sms project sale_management sale payment account_followup sms
    iap mail_enterprise analytic uom odoo_referral odoo_referral_portal
    social_media http_routing web_editor digest contacts_enterprise
    hr_holidays_gantt_calendar account_reports base_setup sale_crm bus
    website_livechat web resource mail calendar fetchmail gamification product
    hr im_livechat portal hr_payroll account_asset hr_holidays website helpdesk
    sale_stock phone_validation sale_timesheet sale_subscription l10n_cr
    """.split(),
}


DEPRECATED = {
    '8.0': "portal"
}


class App(object):
    def __init__(self, args):
        self.args = args
        self.db = psycopg2.connect(self.args.dsn)
        self.cr = self.db.cursor()
        self.version = self.get_odoo_version()
        self.modules_to_clean = self.get_modules_to_clean()

    def posttest(self):
        print(self.args)
        if not self.args.pre_production:
            self.remove_crons()
            self.remove_automations()
            self.remove_mail_servers()
            # self.set_password_v12()
        self.remove_uncertified_data()
        self.clean_actions()
        self.clean_views()
        self.clean_attachments()
        self.group_custom_menus()
        self.delete_obsolete_objects_from_data()
        self.delete_obsolete_actions_server()
        self.handle_attachment_linked_to_unknown_models()
        self.remove_custom_views_without_data()
        self.remove_bank_account_without_partner()
        self.remove_orphan_groups()
        self.clean_menus()
        self.clean_crons()
        self.del_deprecated_models()
        self.apply_queries_needed_spc()

    def clean_menus(self):
        self.cr.execute("""
                        DELETE FROM ir_ui_menu
                        WHERE parent_id IS NULL""")
        self.cr.execute("""
                        DELETE FROM ir_model_data
                        WHERE res_id NOT IN (
                        SELECT id FROM ir_ui_menu) and model = 'ir.ui.menu'""")

    def clean_crons(self):
        self.cr.execute("""
                        DELETE FROM ir_model_data
                        WHERE res_id NOT IN (
                        SELECT id FROM ir_cron) and model = 'ir.cron'""")


    def remove_uncertified_data(self):
        self.cr.execute("ALTER TABLE ir_ui_menu drop CONSTRAINT ir_ui_menu_parent_id_fkey")
        self.cr.execute("""
            ALTER TABLE ir_ui_menu
            ADD CONSTRAINT ir_ui_menu_parent_id_fkey FOREIGN KEY (parent_id)
            REFERENCES ir_ui_menu(id) ON DELETE CASCADE
        """)
        for m in self.modules_to_clean:
            self.module_delete(m)

    def clean_actions(self):
        if self.table_exists('board_board_line'):
            self.cr.execute("""\
                delete from board_board_line
                where action_id in (
                    select id from ir_act_window where view_id not in (
                        select id from ir_ui_view))""")
        if self.table_exists('share_wizard'):
            self.cr.execute("""\
                delete from ir_act_window
                where
                    view_id not in (
                        select id from ir_ui_view)
                    and id not in (
                        select action_id from share_wizard)""")
        else:
            self.cr.execute("""\
                delete from ir_act_window
                where view_id not in (select id from ir_ui_view)""")

    def clean_ir_values(self):
        # if value is not null:
        self.cr.execute("""\
            select distinct(split_part(value,',',1) ) as model
            from ir_values iv where key='action' and value is not null""")

        models = self.dictfetchall()
        for item in models:
            sql = """\
                delete from ir_values
                where
                    split_part(value,',',2)::int not in (
                        select id from %s )
                    and split_part(value,',',1)=%%s""" % (
                        self.model_to_table(item['model']), )
            self.cr.execute(sql, [item['model']])

        # if value is null: check that the object still exists.
        # if not delete ir_value:
        self.cr.execute("""\
            select model from ir_values
            where key='action' and value is null""")
        items = self.dictfetchall()
        for item in items:
            sql = """\
                delete from ir_values
                    where model = %%s
                    and value is null
                    and res_id not in (select id from %s)""" % (
                        self.model_to_table(item['model']), )
            self.cr.execute(sql, [item['model']])

    def clean_views(self):
        if self.table_exists('eco_static_view'):
            self.cr.execute("delete from eco_static_view")
        self.cr.execute("""\
            delete from ir_ui_view
            where id not in (
                select res_id from ir_model_data where model='ir.ui.view') and id not in (SELECT view_template_id FROM payment_acquirer)""")

    def clean_attachments(self):
        self.cr.execute("select distinct(res_model) from ir_attachment")
        for item in self.cr.fetchall():
            self.cr.execute("""\
                SELECT module,id
                from ir_model_data
                where model='ir.model' and name = %s""",
                (item[0],))
            for mod in self.dictfetchall():
                self.cr.execute("""\
                    select state from ir_module_module
                    where name=%s""",
                    (mod['module'],))
                res_state = self.cr.fetchone()
                state = res_state and res_state[0] or False
                if state not in ('installed'):
                    self.cr.execute("""\
                        delete from ir_attachment where model=%s""",
                        (item[0],))

    def remove_magerp_fields(self):
        if self.table_exists('magerp_product_attribute_options'):
            self.cr.execute("""\
                DROP TABLE  magerp_product_attribute_options CASCADE""")
            self.cr.execute("""\
                DELETE FROM ir_model_fields
                WHERE relation = 'magerp.product_attribute_options'""")

    def group_custom_menus(self):
        self.cr.execute("""\
            select id from ir_ui_menu
            where name = 'Custom' and parent_id is null""")
        menu_id = self.cr.fetchone()
        menu_id = menu_id and menu_id[0] or False
        if not menu_id:
            self.cr.execute("""\
                INSERT INTO ir_ui_menu(
                    name,parent_id,sequence
                ) values(
                    'Custom',null,100)
                returning id""")
            menu_id = self.cr.fetchone()[0]

        self.cr.execute("""\
            UPDATE ir_ui_menu im
            set parent_id = %s
            where id not in (
                select res_id from ir_model_data where model='ir.ui.menu')
                    and id != %s """, [menu_id, menu_id,])

        if self.modules_to_clean:
            self.cr.execute("""\
                UPDATE ir_ui_menu im
                set parent_id = %s
                where id in (
                    select res_id from ir_model_data
                    where model='ir.ui.menu'
                        and module in %s
                )
                and id != %s """,
                [menu_id, tuple(self.modules_to_clean), menu_id])

    def delete_obsolete_objects_from_data(self):
        self.cr.execute("""\
            delete from ir_model_data where res_id not in (
                select id from ir_model) and model = 'ir.model'""")

    def delete_obsolete_actions_server(self):
        self.cr.execute("""\
            delete from ir_act_server where id not in (
                select res_id from ir_model_data
                where model = 'ir.actions.server') and
                name in ('Check Account Color Tag',
                         'Create Cost Journal Entry From POS',
                         'Generate Electronic Document',
                         'Ping PAC server')""")

    def delete_obsolete_objects_from_data(self):
        self.cr.execute("""\
            delete from ir_model_data where res_id not in (
                select id from ir_model) and model = 'ir.model'""")

    def handle_attachment_linked_to_unknown_models(self):
        self.cr.execute("""\
            update ir_attachment set res_model = NULL
            where res_model not in (select model from ir_model)""")

    def remove_custom_reports(self):
        self.cr.execute("""\
            update ir_act_report_xml
            set report_rml_content_data = null""")

    def remove_orphan_groups(self):
        self.cr.execute("""\
            delete from res_groups
                where id not in (
                    select res_id from ir_model_data where model = 'res.groups') and
                name='User'""")

    def remove_custom_views_without_data(self):
        # delete views without ir_model_data
        self.cr.execute("""\
            delete from ir_ui_view where id not in (
                select res_id from ir_model_data where model='ir.ui.view')  and id not in (SELECT view_template_id FROM payment_acquirer)""")

    def remove_bank_account_without_partner(self):
        # delete views without ir_model_data
        self.cr.execute("""\
            delete from res_partner_bank
            where partner_id is NULL""")

    def remove_custom_workflows(self):
        self.cr.execute("""\
            delete from wkf where id not in (
                select res_id from ir_model_data
                where model like 'workflow')""")

    def remove_customized_reports(self):
        self.cr.execute("""\
            update ir_act_report_xml set report_rml_content_data=null
            where report_rml_content_data is not null""")
        self.cr.execute("""\
            delete from ir_values
            where split_part(value,',',1)='ir.actions.report.xml'
            and cast(split_part(value,',',2) as int) in (
                select id from ir_act_report_xml where report_type='aeroo')""")

    def remove_mail_servers(self):
        # avoid sending emails during tests
        if self.table_exists('ir_mail_server'):
            self.cr.execute("UPDATE ir_mail_server SET active=False;")
            print('TODO: just inactivate not delete')

    def set_password(self):
        self.cr.execute("""\
            update res_users set login = login || id
            where login = 'admin' and id <> 1""")
        self.cr.execute("""\
            update res_users set login = 'nhomar@vauxoo.com'
            where id = 1""")
        self.cr.execute("""\
            update res_users set password = 'Cl4v3d3M0'
            where id = 1""")

    def set_password_v12(self):
        self.cr.execute("""\
            update res_users set login = 'nhomar@vauxoo.com'
            where id = 2""")
        self.cr.execute("""\
            update res_users set password = 'Cl4v3d3M0'
            where id = 2""")

    def apply_queries_needed_spc(self):
        self.cr.execute("""
            UPDATE ir_module_module SET state = 'to install' WHERE name = 'spc';
            """)
        self.cr.execute("""
            UPDATE ir_module_module SET state = 'uninstalled' WHERE name in (
                'spc_crm_lead_manufacturer', 'spc_account_invoice_line', 'spc_purchase_order', 'spc_manual_move', 'spc_analytic',
                'spc_sale_costs', 'spc_sale_followers', 'spc_crm', 'account_journal_extended_code', 'account_invoice_discount',
                'stock_account_move_line', 'project_task_default_stage', 'stock_requisition_group', 'base_company_prefix',
                'export_fields', 'database_cleanup', 'product_brand');
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'SV-SS' WHERE id = '59';
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'SV-LI' WHERE id = '106';
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'SV-SA' WHERE id = '107';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '52' WHERE state_id = '142';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '52' WHERE state_id = '144';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '57' WHERE state_id = '146';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '57' WHERE state_id = '149';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '52' WHERE state_id = '151';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '56' WHERE state_id = '155';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '54' WHERE state_id = '162';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '53' WHERE state_id = '166';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '54' WHERE state_id = '170';
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'NI-MN' WHERE id = '177';
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'NI-CI' WHERE id = '112';
            """)
        self.cr.execute("""
            UPDATE res_partner SET state_id = '177' WHERE state_id = '113';
            """)
        self.cr.execute("""
            UPDATE res_country_state SET code = 'NI-GR' WHERE id = '114';
            """)
        self.cr.execute("""
            UPDATE calendar_event_type SET name = 'Reunión con proveedores 2' WHERE id = '14';
        """)
        self.cr.execute("""
            UPDATE calendar_event_type SET name = 'Capacitación 2' WHERE id = '12';
        """)
        self.cr.execute("""
            UPDATE calendar_event_type SET name = 'Capacitación 3' WHERE id = '17';
        """)
        self.cr.execute("""
            UPDATE calendar_event_type SET name = 'Llamada telefónica 2' WHERE id = '15';
        """)
        # The product "Minor Line" is now by data
        self.cr.execute("""
            UPDATE
                ir_model_data
            SET
                module = 'spc',
                name = 'product_minor_line',
                noupdate = TRUE,
                date_update = NOW() at time zone 'UTC'
            WHERE
                module = '__export__'
                AND name = 'product_product_44494_771f907d';
        """)



    def remove_constraint(self):
        self.cr.execute("""
            ALTER TABLE payment_acquirer DROP CONSTRAINT payment_acquirer_view_template_id_fkey;
            """)

    def remove_crons(self):
        self.cr.execute("""
            DELETE FROM ir_cron;
            """)

    def remove_automations(self):
        self.cr.execute("""
            DELETE FROM base_automation;
            """)

    # Delete models deprecated in v10.0, they are records that persist
    # after migration
    def del_deprecated_models(self):
        if self.version == '10.0':
            dmodels = DEPRECATED_MODELS[self.version]
            self.cr.execute("""
                DELETE FROM
                    ir_model_constraint
                WHERE
                    model
                IN (SELECT
                        id
                    FROM
                        ir_model
                    WHERE
                        model
                    IN %s
                );""", (dmodels,))

            self.cr.execute("""
                DELETE FROM
                    ir_model_relation
                WHERE
                    model
                IN (SELECT
                        id
                    FROM
                        ir_model
                    WHERE
                        model
                    IN %s
                );""", (dmodels,))
            self.cr.execute(
                "DELETE FROM ir_model WHERE model IN %s",
                (dmodels,))
#
# HELPERS
#

    def dictfetchall(self):
        "Returns all rows from a cursor as a dict"
        desc = self.cr.description
        return [
                dict(zip([col[0] for col in desc], row))
                for row in self.cr.fetchall()
        ]

    def dictfetchone(self):
        "Returns first wow from a cursor as a dict"
        desc = self.cr.description
        result = [
                dict(zip([col[0] for col in desc], [row]))
                for row in self.cr.fetchone()
        ]
        return result[0] if result else dict()

    def get_odoo_version(self):
        guessed_version = self.guess_odoo_version()
        arg_version = self.args.version
        version = arg_version if arg_version else guessed_version
        if not version:
            sys.exit(
                ("Error: no Odoo version found. Please supply the Odoo "
                 "version with the --version command line switch\n"))

        if version not in OUR_MODULES:
            sys.exit((
                ("Error: version '{0}' is not handled by this script. "
                 "Handled versions are: {1}").format(
                    version, ', '.join(sorted(OUR_MODULES.keys())))))

        return version

    def guess_odoo_version(self):
        """Tries to guess Odoo version based on the latest_version column
           of installed modules"""
        version = None
        if self.column_exists('ir_module_module', 'latest_version'):
            self.cr.execute("""
                select coalesce(split_part(latest_version, '.', 1)||'.'||
                split_part(latest_version, '.', 2), 'unknown') as version,
                count(*) from ir_module_module where state = 'installed'
                group by 1 order by 1 desc""")
            versions = self.dictfetchall()
            version = versions[0]['version'] if versions else None

        return version

    def model_to_table(self, model):
        """Get a table name according to a model name"""
        model_table_map = {
            'ir.actions.client': 'ir_act_client',
            'ir.actions.actions': 'ir_actions',
            'ir.actions.report.custom': 'ir_act_report_custom',
            'ir.actions.report.xml': 'ir_act_report_xml',
            'ir.actions.act_window': 'ir_act_window',
            'ir.actions.act_window.view': 'ir_act_window_view',
            'ir.actions.actions': 'ir_act_wizard',
            'ir.actions.url': 'ir_act_url',
            'ir.actions.act_url': 'ir_act_url',
            'ir.actions.server': 'ir_act_server',
            'ir.actions.actions': 'ir_actions',
            'ir.actions.wizard': 'ir_act_wizard',
            'workflow': 'wkf',
            'workflow.activity': 'wkf_activity',
            'workflow.transition': 'wkf_transition',
            'workflow.instance': 'wkf_instance',
            'workflow.workitem': 'wkf_workitem',
            'workflow.triggers': 'wkf_triggers',
            'ir.model.grid': 'ir_model',
            'stock.picking.in': 'stock_picking',
            'stock.picking.out': 'stock_picking',
            'account.report.history': 'account_report',
        }
        if not model:
            model = ''
        return model_table_map.get(model, model).replace('.', '_')

    def module_delete(self, mname):
        print('deleting module {0}'.format(mname))
        self.cr.execute("update ir_module_module set state='uninstalled' where name='%s'" % mname)
        def table_exists(tablename):
            self.cr.execute("SELECT count(1) from information_schema.tables where table_name = %s and table_schema='public'",
                             [tablename])
            return self.cr.fetchone()[0]
        self.cr.execute("select res_id, model from ir_model_data where module=%s and model in %s order by res_id desc", (mname, MODELS_TO_DELETE))
        data_to_delete = self.cr.fetchall()

        for rec in data_to_delete:
            table = self.model_to_table(rec[1])

            self.cr.execute("select count(*) from ir_model_data where model = %s and res_id = %s", [rec[1], rec[0]])
            count1 = self.dictfetchone()['count']
            if count1 > 1:
                continue

            self.cr.execute("savepoint module_delete")
            try:
                # ir_ui_view
                if table == 'ir_ui_view':
                    self.cr.execute('select model from ir_ui_view where id = %s', (rec[0],))
                    t_name = self.cr.fetchone()
                    table_name = t_name and self.model_to_table(t_name[0]) or ''
                    self.cr.execute("select viewname from pg_catalog.pg_views  where viewname = %s", [table_name])
                    if self.cr.fetchall():
                        self.cr.execute('drop view '+table_name +' CASCADE')

                # ir_act_window:
                if table == 'ir_act_window' and table_exists('board_board_line'):
                    self.cr.execute('select count(1) from board_board_line where action_id = %s', (rec[0],))
                    count = self.cr.fetchone()[0]
                    if not count: # yes, there is a bug here. The line is not correctly indented,
                              # but fixing the bug creates some problems after.
                        self.cr.execute('delete from '+table+' where id=%s', (rec[0],))
                elif table == 'ir_model':
                    if table_exists('ir_model_constraint'):
                        self.cr.execute('delete from ir_model_constraint where model=%s', (rec[0],))
                    if table_exists('ir_model_relation'):
                        self.cr.execute('delete from ir_model_relation where model=%s', (rec[0],))
                    #if rec[0] != 440:
                    self.cr.execute('delete from '+table+' where id=%s', (rec[0],))
                # else:
                    # self.cr.execute("delete from audittrail_log_line  where field_id in (4795,4794,4793,4900,4901,4858)")
                    # self.cr.execute("delete from report_multicompany where id = 2")
                #elif table != 'ir_sequence' and rec[0] != 554:
                elif table == 'ir_ui_view':
                    self.delete_views(rec[0])
                else:
                    if table != 'ir_sequence' and rec[0] not in (129, 126):
                        self.cr.execute('delete from '+table+' where id=%s', (rec[0],))

                # also delete dependencies:
                self.cr.execute('delete from ir_module_module_dependency where module_id = %s', (rec[0],))
            except Exception as e:
                last_tb = sys.exc_info()[2]
                tb_msg = traceback.format_exc(last_tb)
                msg = ("Module delete error\n"
                       "Model: {0}, id: {1}\n"
                       "Query: {2}\n"
                       "{3}\n").format(rec[1], rec[0], self.cr.query, tb_msg)
                sys.stderr.write(msg+'\n')
                self.cr.execute("rollback to savepoint module_delete")
            else:
                self.cr.execute("release savepoint module_delete")

        if mname == 'sbd':
            self.cr.execute("delete from ir_model_data where module=%s AND model = 'ir.ui.view'", (mname,))
        else:
            self.cr.execute("delete from ir_model_data where module=%s AND model not in  ('res.country.state.city', 'base.action.rule')", (mname,))
        self.cr.execute('update ir_module_module set state=%s where name=%s', ('uninstalled', mname))

    def delete_views(self, view_id):
        self.cr.execute('select id from ir_ui_view where inherit_id=%d' % view_id)
        views = self.cr.fetchall()
        for view in views:
            self.delete_views(view[0])
        self.cr.execute("""delete from ir_ui_view where id=%d and id not in (SELECT view_template_id FROM payment_acquirer) """ % view_id)

    def table_exists(self, tablename):
        self.cr.execute("SELECT count(1) from information_schema.tables where table_name = %s and table_schema='public'",
                         [tablename])
        return self.cr.fetchone()[0]

    def column_exists(self, table, column):
        self.cr.execute("SELECT count(1)"
            " FROM pg_class c, pg_attribute a"
            " WHERE c.relname=%s"
            " AND c.oid=a.attrelid"
            " AND a.attname=%s", [table, column])
        return self.cr.fetchone()[0]

    def module_rename(self, old_name, new_name):
        # ir_module_module:
        sql = '''select name from ir_module_module where name=%s'''
        self.cr.execute(sql, (new_name, ))
        exists = self.cr.fetchall()

        # ir_module_module_dependency:
        sql = '''update ir_module_module_dependency set name=%s where name=%s'''
        if not exists:
            self.cr.execute(sql, (new_name, old_name))

        if not exists:
            sql = '''update ir_module_module set name=%s where name=%s'''
            self.cr.execute(sql, (new_name, old_name))

        # ir_model_data:

        # module_meta_information could be duplicated in case of a merge:

        sql = """update ir_model_data set module=%s where module=%s and name != 'module_meta_information'"""

        sql_check = "select module, name from ir_model_data where module in %s and name = 'module_meta_information'"
        self.cr.execute(sql_check, [(new_name, old_name)])
        doubles = len(self.cr.fetchall()) > 1
        if doubles:
            sql += " and name != 'module_meta_information'"

        self.cr.execute(sql, (new_name, old_name))

        # set old module as unavailable:
        sql = "update ir_module_module set state = 'uninstallable' where name = %s"
        self.cr.execute(sql, (old_name, ))

    def get_modules_to_clean(self):
        std_modules = OUR_MODULES[self.version]
        to_keep_modules = std_modules

        # eventually add custom modules:
        extract_mod_from_path = lambda x: os.path.split(os.path.split(x)[0])[1]
        for path in self.args.addons_path_list.split(','):
            custom_path = "{0}/*/__manifest__.py".format(path.strip())
            custom_addons = [
                extract_mod_from_path(m) for m in glob.glob(custom_path)]
            to_keep_modules.extend(custom_addons )
        self.cr.execute("""\
            select name from ir_module_module
            where state in ('installed', 'to install', 'to upgrade')""")
        installed_modules = [r[0] for r in self.cr.fetchall() ]
        to_clean_modules = list(
            set(installed_modules).difference(set(to_keep_modules)))

        return to_clean_modules

    def run(self):
        try:
            self.cr.execute('BEGIN')
            self.posttest()
        except Exception as e:
            self.cr.execute('ROLLBACK')
            raise
        except KeyboardInterrupt as e:
            msg = "Program interrupted by user\n"
            sys.stderr.write(msg)
            self.cr.execute('ROLLBACK')
        else:
            if self.args.dry_run:
                self.cr.execute('ROLLBACK')
            else:
                self.cr.execute('COMMIT')


def _main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'dsn',
        help="Database connection string (Data source name)", action='store',
        metavar='DSN')

    parser.add_argument(
        '-a', '--addons-path-list',
        help=("Comma separated list of additional "
              "addons paths (eg: custom modules)"),
        action='store', default='')

    parser.add_argument(
        '--version',
        help="Odoo version of the modules",
        action='store', default='13.0')

    parser.add_argument(
        '--dry-run',
        help="Do not actually change anything; just print the sql statements",
        action='store_true', default=False)

    parser.add_argument(
        '-v', '--verbose', help="Verbose output.", dest="verbose",
        action='append_const', const=1)

    parser.add_argument(
        '-p', '--pre-production', help="Run Preproduction part only",
        dest="pre_production", action='append_const', const=1)

    args = parser.parse_args()

    app = App(args)
    app.run()


if __name__ == '__main__':
    _main()
