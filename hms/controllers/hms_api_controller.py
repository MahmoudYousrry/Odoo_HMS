from odoo import http
from odoo.http import request

class HmsPatientController(http.Controller):

    @http.route('/hms/patients', type='json', auth='none', csrf=False)
    def get_patients(self):
        try:
            patients = request.env['hms.patient'].sudo().search([])
            if not patients:
                return {
                    "message": "There are no records",
                }

            return [{
                'id': p.id,
                'first_name': p.first_name,
                'last_name': p.last_name,
                'name': f"{p.first_name} {p.last_name}",
                'email': p.email,
                'birth_date': p.birth_date.strftime('%Y-%m-%d') if p.birth_date else None,  # تحويل التاريخ لstring
                'history': p.history if p.history else '',  # Medical History (HTML)
                'pcr': p.pcr,  # Boolean
                'cr_ratio': p.cr_ratio,  # Float
                'blood_type': p.blood_type,  # Selection
                'image': p.image if p.image else None,  # الصورة (base64 encoded)
                'address': p.address if p.address else '',
                'age': p.age,
                'department_id': p.department_id.id if p.department_id else None,
                'department_name': p.department_id.name if p.department_id else 'N/A',  # اسم القسم
                'department_capacity': p.department_capacity,
                'doctor_ids': [(doc.id, doc.name) for doc in p.doctor_ids],  # لستة من الأطباء (id, name)
                'log_history_ids': [(log.id, log.create_date.strftime('%Y-%m-%d %H:%M:%S')) for log in p.log_history_ids],  # لستة من السجلات
                'state': p.state,
            } for p in patients]

        except Exception as error:
            return {
                "message": str(error),
            }


    @http.route('/hms/patients/<int:patient_id>/delete', type='json', auth='none', csrf=False, methods=['POST'])
    def delete_patient(self, patient_id):
        try:
            patient = request.env['hms.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return {"error": "Patient not found."}
            patient.unlink()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
