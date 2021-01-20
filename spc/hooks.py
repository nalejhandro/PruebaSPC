from odoo import api, SUPERUSER_ID


def restore_procurement_rules_active_state(cr, env):
    def _make_import(contents):
        return env['base_import.import'].create({
            'res_model': 'base_import.tests.models.complex',
            'file_name': 'f',
            'file_type': 'text/csv',
            'file': contents,
        })

    attach = env['ir.attachment'].search([
        ('name', '=', 'procurement.rule.csv')])
    if attach:
        data = _make_import(
            attach.index_content.encode('utf-8'))._convert_import_data(
                ['id', 'active'], {'quoting': '"', 'separator': ',', 'headers': True})[0]
        for line in data:
            item = env.ref(line[0], False)
            if item:
                item.write({
                    'active': line[1] == 'True'
                })


def update_duplicated_analytic_accounts(cr, env):
    res = env['account.analytic.account'].read_group(
        [], fields=["ids:array_agg(id)"], groupby=['name', 'company_id'], lazy=False)
    duplicateds = [a for a in res if a['__count'] > 1]
    for item in duplicateds:
        for account in env['account.analytic.account'].browse(item['ids']):
            name = "%s-%s" % (account.name, account.id)
            env.cr.execute("UPDATE account_analytic_account SET name=%s WHERE id = %s", (name, account.id))
    env['ir.rule'].search([
        ('name', '=', 'Project: multi-company'),
        ('model_id', '=', env.ref('helpdesk.model_helpdesk_team').id)
    ]).write({'domain_force': "['|', ('company_id', '=', False), ('company_id', 'child_of', [user.company_id.id])]"})


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_duplicated_analytic_accounts(cr, env)
    restore_procurement_rules_active_state(cr, env)
