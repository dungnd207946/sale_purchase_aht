/** @odoo-module **/
import { FormRenderer } from "@web/views/form/form_renderer"
import { patch } from "@web/core/utils/patch";
import { CustomStatusBar } from "@workflow/custom_status_bar/custom_status_bar";

patch(FormRenderer, {
    components: {
       ...FormRenderer.components || {},
       CustomStatusBar,
    },
})