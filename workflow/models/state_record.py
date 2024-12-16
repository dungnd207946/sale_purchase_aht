from odoo import models, fields, api, exceptions

class StateRecord(models.Model):
    _name = 'state.record'
    _description = 'State Record'
    workflow_id = fields.Many2one('custom.workflow', string='Workflow', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    record_id = fields.Integer(string='Record in Model', ondelete='cascade')
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
            # Giới hạn model bị check chỉ có trong workflow
            models_to_check = self.env['custom.workflow'].search([]).mapped('model_id.model')
            if model in models_to_check:
                # Lấy workflow của model chứa bản ghi này
                workflow = self.env['custom.workflow'].search([
                    ('model_id.model', '=', model),
                    ('companies_id', 'in', [self.env.company.id]),
                ], limit=1)
                if not workflow:
                    raise exceptions.UserError("Company hoặc Model hiện tại chưa có workflow!")
                # Trong workflow này, check xem state tiếp theo có quyền truy cập hay không
                if not self._is_state_valid(new_state, workflow):
                    raise exceptions.UserError("Người dùng hiện tại không có quyền truy cập!")
                else:
                    print("Write new state")
                    # Cập nhật trạng thái mới cho bản ghi
                    record.write({'state': new_state})
        else:
            print("Update state fail")

    def _is_state_valid(self, state, workflow):
        print("Call valid state")
        workflow_state = self.env['custom.workflow.state'].search([('workflow_id', '=', workflow.id),
                                                                   ('state.name', '=', state)
                                                                   ], limit=1)

        if not workflow_state:
            raise exceptions.UserError("State chưa được khai báo trong workflow!")
        state_groups = workflow_state.approve_user
        user_groups = self.env.user.groups_id
        if user_groups & state_groups:  # Kiểm tra giao nhau của 2 danh sách nhóm
            return True
        return False

    @api.model
    def new_state_for_new_record(self, model, record_id):
        model_id = self.env['ir.model'].search([('model', '=', model)], limit=1)
        workflow_id = self.env['custom.workflow'].search([('model_id', '=', model_id.id)], limit=1)
        if workflow_id:
            state_value = workflow_id.custom_state[0].state.name if workflow_id.custom_state else ''
            self.create({
                'workflow_id': workflow_id.id,
                'model_id': model_id.id,
                'record_id': int(record_id),
                'state': state_value
            })