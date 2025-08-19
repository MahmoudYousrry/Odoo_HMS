from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import ValidationError


class TestInsuranceCompany(TransactionCase):

    def setUp(self):
        super(TestInsuranceCompany, self).setUp()

        self.insurance_company = self.env['insurance.company'].create({
            'name': 'Care Insurance',
            'coverage_percentage': 80.0,
            'phone': '+1234567890',
            'email': 'info@care.com',
            'website': 'https://www.care.com',
        })

    def test_check_insurance_company_fields(self):
        """
        Test that the insurance company fields are correctly set upon creation.
        """
        self.assertEqual(self.insurance_company.name, 'Care Insurance', "Insurance company name does not match")
        self.assertEqual(self.insurance_company.coverage_percentage, 80.0, "Coverage percentage does not match")
        self.assertEqual(self.insurance_company.phone, '+1234567890', "Phone number does not match")
        self.assertEqual(self.insurance_company.email, 'info@care.com', "Email does not match")
        self.assertEqual(self.insurance_company.website, 'https://www.care.com', "Website does not match")
        self.assertTrue(self.insurance_company.partner_id, "Partner should be auto-created")
        self.assertEqual(self.insurance_company.partner_id.name, 'Care Insurance', "Partner name mismatch")

    def test_invalid_coverage_percentage_raises_error(self):
        """
        Test that creating an insurance company with invalid coverage percentage raises ValidationError.
        """
        with self.assertRaises(ValidationError):
            self.env['insurance.company'].create({
                'name': 'Invalid Insurance',
                'coverage_percentage': 150.0,
            })
