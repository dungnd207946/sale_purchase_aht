/** @odoo-module */

import { FormCompiler } from "@web/views/form/form_compiler";
import { CustomStatusBar } from "./custom_status_bar/custom_status_bar";
import {mount, whenReady} from "@odoo/owl";
import { templates } from "@web/core/assets";
import { patch } from "@web/core/utils/patch";
import {
    append,
    combineAttributes,
    createElement,
    createTextNode,
    getTag,
} from "@web/core/utils/xml";


patch(FormCompiler.prototype, {
    compileHeader(el, params) {
        console.log("Call custom Header")
        const statusBar = super.compileHeader(el, params);
        const customHeader = document.createElement("div");
        customHeader.id = "custom-status-bar-header";
        let customStatusBar = createElement("CustomStatusBar");
        append(customHeader, customStatusBar)
        // mount(CustomStatusBar, customHeader, { props: {}, templates, dev: true, name: "Custom Bar" });

        append(customHeader, statusBar)
        return customHeader;

    }
})