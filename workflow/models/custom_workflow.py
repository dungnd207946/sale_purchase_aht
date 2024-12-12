from odoo import models, fields, api

class CustomWorkflow(models.Model):
    _name = 'custom.workflow'
    _description = 'Custom Workflow'
    name = fields.Char(string='Name')
    model_id = fields.Many2one('ir.model', string='Model', unique=True, required=True, ondelete='cascade')
    _sql_constraints = [
        ('unique_model', 'unique(model_id)', 'The Model must be unique!'),
    ]
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    companies_id = fields.Many2many('res.company', 'workflow_company_rel', string='Company')
    custom_state = fields.One2many('custom.workflow.state', 'workflow_id', string='State')

    @api.model
    def get_states_by_model(self, model):
        print(model)
        workflow = self.search([('model_id.model', '=', model)], limit=1)
        if workflow:
            state_records = self.env['custom.workflow.state'].search([('workflow_id', '=', workflow.id)])
            sorted_states = sorted(state_records, key=lambda s: s.priority, reverse=True)
            states = {
                s.state: {
                    "value": s.state,
                    "label": s.state,
                    "priority": s.priority
                }
                for s in sorted_states
            }
            return states


    @api.model
    def create(self, vals):
        record = super(CustomWorkflow, self).create(vals)
        # Vấn đề: nó chỉ tạo record cho các bản ghi đã tồn tại !
        model_records = self.env[record.model_id.model].search([])

        for m in model_records:
            state_value = record.custom_state[0].state if record.custom_state else ''
            self.env['state.record'].create({
                'workflow_id': record.id,
                'model_id': record.model_id.id,
                'record_id': int(m.id),
                'state': state_value
            })

        return record



