/** @odoo-module **/

import { Component } from '@odoo/owl';

export class OwlComponent extends Component {
    static template = "custom_owl_module.TemplateOwlExample";

    // Component state
    constructor() {
        super(...arguments);
        this.state = {
            counter: 0,
        };
    }

    increment() {
        this.state.counter++;
    }
}
