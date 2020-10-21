from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    res = env['account.analytic.account'].read_group(
        [], fields=["ids:array_agg(id)"], groupby=['name', 'company_id'], lazy=False)
    duplicateds = [a for a in res if a['__count'] > 1]
    for item in duplicateds:
        for account in env['account.analytic.account'].browse(item['ids']):
            name = "%s-%s" % (account.name, account.id)
            env.cr.execute("UPDATE account_analytic_account SET name=%s WHERE id = %s", (name, account.id))
