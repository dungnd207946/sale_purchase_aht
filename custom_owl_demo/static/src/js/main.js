// /** @odoo-module **/
//
// odoo.define('custom_owl_demo.main', function (require) {
//     "use strict";
//
//     const { Component, useState } = owl
//
//     // Define a simple OWL component
//     class TodoList extends Component {
//         constructor() {
//             super(...arguments);
//             this.state = useState({
//                 tasks: ['Task 1', 'Task 2'],
//                 newTask: ''
//             });
//         }
//
//         // Method to add a new task
//         addTask() {
//             if (this.state.newTask) {
//                 this.state.tasks.push(this.state.newTask);
//                 this.state.newTask = '';
//             }
//         }
//
//         // Render method to display the tasks
//         render() {
//             return this._renderTemplate(`
//                 <div>
//                     <h3>Todo List</h3>
//                     <ul>
//                         <li t-foreach="state.tasks" t-as="task">
//                             <span t-esc="task"/>
//                         </li>
//                     </ul>
//                     <input t-model="state.newTask" placeholder="New task" />
//                     <button t-on-click="addTask">Add Task</button>
//                 </div>
//             `);
//         }
//     }
//
//     // Mount the component to the DOM
//     const app = new TodoList();
//     app.mount(document.body);
// });
//
