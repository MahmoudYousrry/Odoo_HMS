/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

import { OrdersList } from "./orders_list";

export class ClientAction extends Component {
    static template = "hms.ClientActionTemplate";
}

ClientAction.components = {
    OrdersList,
};

registry.category("actions").add("hello.client.action", ClientAction);
