#    Copyright 2016 MATMOZ, Slovenia (Matjaž Mozetič)
#    Copyright 2018 EFICENT (Jordi Ballester Alomar)
#    Copyright 2018 LUXIM, Slovenia (Matjaž Mozetič)
#    Together as the Project Expert Team
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class DeliverablePlanLineChangeState(models.TransientModel):

    _name = "deliverable.plan.line.change.state"
    _description = "Change state of deliverable plan line"

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed')
        ],
        'Status',
        index=True,
        required=True,
        help=' * The \'Draft\' status is used when a user is encoding '
             'a new and unconfirmed deliverable plan line. '
             '\n* The \'Confirmed\' status is used for to confirm the '
             'deliverable plan line by the user.'
    )

    @api.multi
    def change_state_confirm(self):
        data = self[0]
        record_ids = self._context and self._context.get('active_ids', False)
        line_plan = self.env['analytic.deliverable.plan.line'].browse(record_ids)
        new_state = data.state if data and data.state else False
        if new_state == 'draft':
            line_plan.action_button_draft()
        elif new_state == 'confirm':
            line_plan.filtered(
                lambda r: r.parent_id.id is False).action_button_confirm()
        return {
            'domain': "[('id','in', [" + ','.join(
                map(str, record_ids)
            ) + "])]",
            'name': _('Deliverable Planning Lines'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'analytic.deliverable.plan.line',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
