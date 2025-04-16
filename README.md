# Hospital Management System (HMS) - Odoo 18

## Overview  
The **Hospital Management System (HMS)** is an Odoo 18 module designed to manage hospital operations, including patient records, doctors, departments, and user access control.  

## Features  

### Patients Management  
- Create, read, update, and delete patient records.  
- Auto-calculate patient age from birthdate.  
- Unique and valid email addresses for patients.  
- Patient status tracking (Undetermined, Good, Fair, Serious).  
- Log history for patient actions.  

### Doctors & Departments  
- Manage doctors and their profiles.  
- Link doctors to departments and patients.  
- Restrict patient assignment to open departments only.  
- Show department capacity in the patient view.  

### CRM Integration  
- Link patients with customers in the CRM.  
- Prevent deleting customers linked to patients.  
- Enforce unique email constraints between CRM customers and patients.  

### Access Control  
- **User Role**  
  - Can manage their own patient records.  
  - Can view departments and doctors but not edit them.  
- **Manager Role**  
  - Full CRUD access to patients, doctors, and departments.  
  - Can view doctors' details and manage all records.  

### Reports & UI Enhancements  
- Custom patient status report generation.  
- Improved list view for customers (showing website field).  
- Mandatory Tax ID field for CRM customers.  

### Owl Patients List UI  
- Added a custom Owl.js component to list all patients.  
- Includes:
  - Patient cards with name, age, email, and status.  
  - Modal popup for full patient details (including image, medical history, and department info).  
  - Delete functionality with confirmation.  
- Responsive and user-friendly UI powered by OWL + Bootstrap.  

## Installation  
1. Clone this repository into your Odoo addons directory:  
   ```sh
   git clone https://github.com/MahmoudYousry/Odoo_HMS.git
   ```
2. Restart Odoo and update the module list:  
   ```sh
   ./odoo-bin --addons-path=addons/ -u hms
   ```
3. Install the module from the Odoo Apps menu.  

## Usage  
- Navigate to **Hospital Management** under the main menu.  
- Manage **Patients, Doctors, and Departments**.  
- Assign patients to doctors and track their medical history.  
- Generate **patient reports** from the system.  

## License  
This module is released under the MIT License.

