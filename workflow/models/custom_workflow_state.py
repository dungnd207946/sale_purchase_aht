from odoo import models, fields, api

class CustomWorkflowState(models.Model):
    _name = 'custom.workflow.state'
    _description = 'Custom Workflow State'
    workflow_id = fields.Many2one('custom.workflow', string='Workflow')
    state = fields.Char(string='Next State', help='The state which user aim to reach')
    priority = fields.Integer(string='Priority', unique=True)
    approve_user = fields.Many2many('res.groups', relation='state_groups_rel', string='Available Group User')

    _sql_constraints = [
        ('unique_priority', 'unique(priority, workflow_id)', 'Priority must be unique!'),
    ]
    @api.model
    def _update_state_record(self):
        """
        Helper function to update state in state.record for all related records.
        """
        print("Call update state record")
        for state in self:
            # Lấy giá trị đầu tiên của state trong workflow
            first_state = self.env['custom.workflow.state'].search([('workflow_id', '=', state.workflow_id.id)], limit=1)
            first_state_value = first_state.state if first_state else ''

            # Cập nhật tất cả state.record trong workflow (model) này
            state_records = self.env['state.record'].search([('workflow_id', '=', state.workflow_id.id)])
            for record in state_records:
                record.write({'state': first_state_value})

    @api.model
    def write(self, vals):
        """
        Override write to handle state updates.
        """
        result = super(CustomWorkflowState, self).write(vals)

        if 'state' in vals:
            self._update_state_record()

        return result

    @api.model
    def unlink(self):
        workflow_ids = self.mapped('workflow_id.id')
        result = super(CustomWorkflowState, self).unlink()
        for workflow_id in workflow_ids:
            # Lấy state đầu tiên của workflow_id
            first_state = self.env['custom.workflow.state'].search([('workflow_id', '=', workflow_id)], limit=1)
            first_state_value = first_state.state if first_state else ''

            # Cập nhật tất cả các bản ghi trong state.record có workflow_id tương ứng
            state_records = self.env['state.record'].search([('workflow_id', '=', workflow_id)])
            for record in state_records:
                record.write({'state': first_state_value})  # Cập nhật lại state
        return result