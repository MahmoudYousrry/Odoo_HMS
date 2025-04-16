/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class OrdersList extends Component {
    static template = "hms.OrdersListTemplate";

    setup() {
        this.state = useState({ patients: [] });
        this.fetchPatients();
    }

    async fetchPatients() {
        try {
            const data = await rpc('/hms/patients');
            this.state.patients = data;
        } catch (error) {
            console.error("Error fetching patients:", error);
        }
    }

    viewPatient(id) {
        const patient = this.state.patients.find(p => p.id === id);
        if (patient) {
            this.state.selectedPatient = patient;
            const modal = new bootstrap.Modal(document.getElementById('patientModal'));
            modal.show();
        }
    }

    async deletePatient(id) {
        if (!confirm("Are you sure you want to delete this patient?")) return;

        try {
            await rpc(`/hms/patients/${id}/delete`, { method: 'POST' });
            this.state.patients = this.state.patients.filter(p => p.id !== id);
        } catch (error) {
            console.error("Delete error:", error);
        }
    }
}
