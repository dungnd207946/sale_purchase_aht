/** @odoo-module */
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CustomStatusBar extends Component {
    static template = "workflow.CustomStatusBar"
    setup(){
        this.states = useState([
        ]);
        this.orm = useService('orm');
        this.getStates();
        this.create_state_for_new_record()
    }


    async getStates(){
        console.log("Call get state")
        const res_model = await this.env.model.root.resModel;
        const res_id = await this.env.model.root.resId;
        const model = String(res_model)

        // Tất cả state của model
        const model_state = await this.orm.call('custom.workflow', 'get_states_by_model', [model]);
        console.log(model_state)
        // State hiện tại của bản ghi
        const record_state = await this.orm.call('state.record', 'get_state_by_resID', [res_id, model]);
        console.log(record_state)
        if (model_state) {
            const stateArray = Object.values(model_state);  // Chuyển đổi đối tượng thành mảng
            // Cập nhật dữ liệu vào this.states
            const newStates = [];
            stateArray.forEach((item, index, array) => {
                newStates.push({
                    value: item.value,
                    label: item.label.charAt(0).toUpperCase() + item.label.slice(1),
                    priority: item.priority,
                    isSelected: record_state == item.value,
                    item_first: index === 0,
                    item_last: index === array.length - 1,
                });
            });
            this.states.push(...newStates);
        } else {
            console.log("No state");
        }
    }
    async approve_state() {
        console.log("Approve");
        const res_id = await this.env.model.root.resId;
        const res_model = await this.env.model.root.resModel;

        let previousState = null;
        for (const [index, state] of this.states.entries()) {
            if (state.isSelected && index > 0) {
                if (previousState) {
                    await this.orm.call('state.record', 'update_state', [res_id, res_model, previousState.value]);
                    previousState.isSelected = true;
                    state.isSelected = false;
                }
            }
            previousState = state;
        }
    }

    async cancel_state() {
        console.log("Cancel button");
        const res_id = await this.env.model.root.resId;
        const res_model = await this.env.model.root.resModel;

        let nextState = false;
        let previousState = null;

        for (const state of this.states) {
            if (nextState) {
                await this.orm.call('state.record', 'update_state', [res_id, res_model, state.value]);
                previousState.isSelected = false;
                state.isSelected = true;
                console.log("Call break ")
                break;
            }
            if (state === this.states[this.states.length - 1]) {
                break;
            }
            if (state.isSelected && nextState === false) {
                nextState = true;
            }
            previousState = state
        }
    }

    async create_state_for_new_record() {
        console.log("Create state for new record");
        const res_id = await this.env.model.root.resId;
        const res_model = await this.env.model.root.resModel;

        const existingWorkflow = await this.orm.searchRead('custom.workflow', [['model_id.model', '=', res_model]], ['id']);
        if (existingWorkflow.length === 0) {
            console.log(`No workflow found for model: ${res_model}`);
            return; // Không có workflow, thoát ra
        }

        // Đã có res ID rồi nhưng không tồn tại record
        const existingState = await this.orm.searchRead('state.record', [
                ['model_id.model', '=', res_model],
                ['record_id', '=', res_id]
            ], ['id']);

        if (existingState.length > 0) {
            console.log(`State record already exists for model: ${res_model}, res_id: ${res_id}`);
            return; // Đã có state.record, không cần tạo mới
        }
        await this.orm.call('state.record', 'new_state_for_new_record', [res_model, res_id]);
    }

}

// registry.category("components").add("CustomStatusBar", CustomStatusBar);