from odoo import models, exceptions

class CustomBaseModel(models.AbstractModel):
    _inherit = 'base'

    def write(self, vals):
        print("Call in custom Base")
        models_to_check = ['sale.order', 'purchase.order', 'custom.workflow']
        if self._name in models_to_check and 'state' in vals:
            # Kiểm tra điều kiện state
            for record in self:
                current_model = record._name
                print(current_model)
                workflow = self.env['custom.workflow'].search([
                    ('model_id.model', '=', current_model),
                    ('companies_id', 'in', [self.env.company.id]),
                ], limit=1)
                if not workflow:
                    raise exceptions.UserError("Workflow is not exist with current company or model!")
                # Kiểm tra xem model hiện tại có trường state hay không
                if hasattr(record, 'state'):
                #     current_state = getattr(record, 'state', None)
                # Bỏ current state
                    state = vals['state']
                    if not self._is_state_valid(state, workflow):
                        raise exceptions.UserError("Current user right is not available for this action!")

        return super(CustomBaseModel, self).write(vals)

    def _is_state_valid(self, state, workflow):
        print("Call valid state")
        workflow_state = self.env['custom.workflow.state'].search([('workflow_id', '=', workflow.id),
                                                                   ('state', '=', state)
                                                                   ], limit=1)

        if not workflow_state:
            raise exceptions.UserError("Current state workflow is not authorized!")
        state_groups = workflow_state.approve_user
        user_groups = self.env.user.groups_id
        if user_groups & state_groups:  # Kiểm tra giao nhau của 2 danh sách nhóm
            return True
        return False
