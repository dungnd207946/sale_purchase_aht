from odoo import models, exceptions

class CustomBaseModel(models.AbstractModel):
    _inherit = 'base'

    def write(self, vals):
        print("Call in custom Base")
        # Vì trong state.record có trường state, trùng tên với state của các trường khác
        models_not_to_checks = ['state.record']
        if self._name not in models_not_to_checks and 'state' in vals:
            # Kiểm tra điều kiện state
            for record in self:
                current_model = record._name
                print(current_model)
                workflow = self.env['custom.workflow'].search([
                    ('model_id.model', '=', current_model),
                    ('companies_id', 'in', [self.env.company.id]),
                ], limit=1)
                if not workflow:
                    raise exceptions.UserError("Company hoặc Model hiện tại chưa có workflow!")
                # Kiểm tra xem model hiện tại có trường state hay không
                if hasattr(record, 'state'):
                    state = vals['state']
                    if not self.is_state_valid(state, workflow):
                        raise exceptions.UserError("Người dùng hiện tại không có quyền truy cập!")

        return super(CustomBaseModel, self).write(vals)

    def is_state_valid(self, state, workflow):
        print("Call valid state")
        workflow_state = self.env['custom.workflow.state'].search([('workflow_id', '=', workflow.id),
                                                                   ('state', '=', state)
                                                                   ], limit=1)

        if not workflow_state:
            raise exceptions.UserError("State chưa được khai báo trong workflow!")
        state_groups = workflow_state.approve_user
        user_groups = self.env.user.groups_id
        if user_groups & state_groups:  # Kiểm tra giao nhau của 2 danh sách nhóm
            return True
        return False
