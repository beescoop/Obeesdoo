from odoo.exceptions import ValidationError

from .test_volunteer_common import TestVolunteerCommon


class TestShiftParticipation(TestVolunteerCommon):
    def setUp(self):
        super().setUp()

    def test_max_volunteer_lower_than_confirmed_participations(self):
        """Test if participation is prohibited when the max_volunteer_nb
        is lower than the number of confirmed participations
        3 participations confirmed, max_volunteer_nb = 2
        participation refused"""

        self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Participation.create(
                {
                    "volunteer_id": self.volunteer_test.id,
                    "shift_id": self.shift_max_2.id,
                    "registration_state": "confirmed",
                }
            )
