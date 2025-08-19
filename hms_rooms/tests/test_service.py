from odoo.tests.common import TransactionCase

class TestRoomService(TransactionCase):

    def test_create_service(self):
        service = self.env['room.service'].create({
            'service_name': 'Test Service',
            'price': 20.0,
            'service_type': 'basic',
        })
        self.assertTrue(service.id, "Room Service should be created successfully")
