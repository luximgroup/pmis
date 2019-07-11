#    Copyright 2016 MATMOZ, Slovenia (Matjaž Mozetič)
#    Copyright 2018 EFICENT (Jordi Ballester Alomar)
#    Copyright 2018 LUXIM, Slovenia (Matjaž Mozetič)
#    Together as the Project Expert Team
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_debit_credit_bal_qtty_plan(self):
        analytic_line_obj = self.env['account.analytic.line.plan']
        domain = [('account_id', 'in', self.mapped('id'))]
        if self._context.get('from_date', False):
            domain.append(('date', '>=', self._context['from_date']))
        if self._context.get('to_date', False):
            domain.append(('date', '<=', self._context['to_date']))

        account_amounts = analytic_line_obj.search_read(
            domain, ['account_id', 'amount']
        )
        account_ids = set(
            [line['account_id'][0] for line in account_amounts]
        )
        data_debit_plan = {account_id: 0.0 for account_id in account_ids}
        data_credit_plan = {account_id: 0.0 for account_id in account_ids}
        for account_amount in account_amounts:
            if account_amount['amount'] < 0.0:
                data_debit_plan[
                    account_amount['account_id'][0]
                ] += account_amount['amount']
            else:
                data_credit_plan[
                    account_amount['account_id'][0]
                ] += account_amount['amount']

        for account in self:
            account.debit_plan = abs(data_debit_plan.get(account.id, 0.0))
            account.credit_plan = data_credit_plan.get(account.id, 0.0)
            account.balance_plan = account.credit_plan - account.debit_plan

    @api.multi
    def _compute_debit_credit_balance(self):
        """
        Warning, this method overwrites the standard because the hierarchy
        of analytic account changes
        """
        super(
            AccountAnalyticAccount, self)._compute_debit_credit_balance()
        analytic_line_obj = self.env['account.analytic.line.plan']
        # compute only analytic line
        for account in self.filtered(lambda x: x.child_ids):
            domain = [('account_id', 'child_of', account.ids)]
            credit_groups = analytic_line_obj.read_group(
                domain=domain + [('amount', '>', 0.0)],
                fields=['account_id', 'amount'],
                groupby=['account_id']
            )
            data_credit_plan = sum(l['amount'] for l in credit_groups)
            debit_groups = analytic_line_obj.read_group(
                domain=domain + [('amount', '<', 0.0)],
                fields=['account_id', 'amount'],
                groupby=['account_id']
            )
            data_debit_plan = sum(l['amount'] for l in debit_groups)
            account.debit_plan = abs(data_debit_plan)
            account.credit_plan = data_credit_plan
            account.balance_plan = account.credit_plan - account.debit_plan

    plan_line_ids = fields.One2many(
        'account.analytic.line.plan',
        'account_id',
        string="Analytic Entries"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    balance_plan = fields.Float(
        compute='_compute_debit_credit_bal_qtty_plan',
        string='Planned Balance'
    )
    debit_plan = fields.Float(
        compute='_compute_debit_credit_bal_qtty_plan',
        string='Planned Debit'
    )
    credit_plan = fields.Float(
        compute='_compute_debit_credit_bal_qtty_plan',
        string='Planned Credit'
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
        readonly=True
    )
    plan_line_count = fields.Integer(
        compute='_compute_plan_line_count', type='integer'
    )

    @api.depends('plan_line_ids')
    def _compute_plan_line_count(self):
        for record in self:
            record.plan_line_count = len(record.plan_line_ids)
