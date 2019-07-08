from odoo import fields, models


class PurchaseLine(models.Model):

    _inherit = 'purchase.order.line'

    resource_id = fields.Many2one(
        comodel_name='analytic.resource.plan.line',
        string='Resources'
    )
