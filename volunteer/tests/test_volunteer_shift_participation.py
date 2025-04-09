from odoo.exceptions import ValidationError

from .test_volunteer_common import TestVolunteerCommon


class TestShiftParticipation(TestVolunteerCommon):
    def setUp(self):
        super().setUp()

    def test_participation_refused_when_shift_full(self):
        """Test that a participation is refused when the number of confirmed
        participation exceeds max_volunteer_nb.
        3 participation confirmed, max_volunteer_nb = 2
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
