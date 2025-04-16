{
    "name":"Hospital_MS",
    "author":"MahYousry",
    "description":"Hospital Managment System",
    "data" : [
        "security/hms_security.xml",
        "security/ir.model.access.csv",
        "views/hms_patient_view.xml",
        "views/hms_department_view.xml",
        "views/hms_doctor_view.xml",
        "reports/hms_patient_report.xml"
    ],
    'assets': {
    'web.assets_backend': [
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
        'hms/static/src/components/patient_owl/js/*.js',
        'hms/static/src/components/patient_owl/xml/*.xml',

    ],
},
}