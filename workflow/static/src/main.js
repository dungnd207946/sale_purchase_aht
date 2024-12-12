// /** @odoo-module **/
//
//
// import {mount, useState, whenReady} from "@odoo/owl";
// import { Playground } from "@awesome_owl/playground";
// import { registry } from "@web/core/registry";
// import { patch } from "@web/core/utils/patch";
//
// console.log("Test global Custom JS")
// patch(Playground.prototype,{
//     setup(){
//         super.setup();
//         this.sum = useState({ value: 5 })
//     },
//     incrementSum(){
//         console.log("Call custom increase")
//         this.sum.value += 3;
//     },
// });