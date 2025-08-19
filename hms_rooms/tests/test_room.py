from odoo.tests.common import TransactionCase

class TestRoom(TransactionCase):

    def test_create_room(self):
        room = self.env['room'].create({
            'room_type': 'standard',
            'clinic_id': self.env['clinic'].create({'name': 'Test Clinic'}).id,
            'bed_count': 2,
            'base_hourly_price': 50.0,
        })
        self.assertTrue(room.id, "Room should be created successfully")
