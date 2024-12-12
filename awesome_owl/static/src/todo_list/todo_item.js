/** @odoo-module **/
import { Component, useState } from "@odoo/owl"

export class TodoItem extends Component {
    static template = "awesome_owl.TodoItem"
    static props = {
        todo: {
            type: Object,
            shape: { id: Number, description: String, isCompleted: Boolean }
            // Khai báo này chỉ ra rằng, khi truyền dữ liệu từ component cha (trong xml) vào thì cần viết đúng kiểu dữ liệu này
            // Ví dụ: <TodoItem todo="{ id: 1, description: 'Write code', isCompleted: false }" />
        },
        toggleState: Function,
        removeItem: Function,
    };

    onChange() {
        this.props.toggleState(this.props.todo.id);
    }

    onRemove() {
        this.props.removeItem(this.props.todo.id);
    }
}