from odoo import models, fields, api

class StateRecord(models.Model):
    _name = 'state.record'
    _description = 'State Record'
    workflow_id = fields.Many2one('custom.workflow', string='Workflow', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model')
    record_id = fields.Integer(string='Record in Model')
    state = fields.Char(string='Current state')

    @api.model
    def get_state_by_resID(self, resID, model):
        resID = int(resID)
        record = self.search([('model_id.model', '=', model), ('record_id', '=', resID)], limit=1)
        return record.state

    @api.model
    def update_state(self, resID, model, new_state):
        resID = int(resID)
        record = self.search([('model_id.model', '=', model), ('record_id', '=', resID)], limit=1)
        if record:
            # Cập nhật trạng thái mới cho bản ghi
            record.write({'state': new_state})
        else:
            print("Update state fail")

    @api.model
    def new_state_for_new_record(self, model, record_id):
        model_id = self.env['ir.model'].search([('model', '=', model)], limit=1)
        workflow_id = self.env['custom.workflow'].search([('model_id', '=', model_id.id)], limit=1)
        if workflow_id:
            state_value = workflow_id.custom_state[0].state if workflow_id.custom_state else ''
            self.create({
                'workflow_id': workflow_id.id,
                'model_id': model_id.id,
                'record_id': int(record_id),
                'state': state_value
            })