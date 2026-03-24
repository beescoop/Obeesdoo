- Currently, shifts that were canceled due to company holidays are not marked as such. It can be a source of confusion.

Suggestion: Add message in the chatter of the shift form view stating that it was canceled because of company holidays.

- A label indicates whether a shift overlaps with any holiday period ONLY in the shift form view.

Suggestion: Add the same label in all shift views, especially in the shift list view.

- No reminder that a shift has been created through a Generator with the bool is_maintained_during_holiday=True is visible on the shift. 

Suggestion: Add a field to the volunteer shift model and views to show this information.

- Currently, there is no warning or any form of control in the cancellation-of-shifts-due-to-holidays process.

Suggestions:
Add a wizard to control every step of the process when creating company holidays.
Add a button in the company holidays view that would allow to trigger the function that cancels shifts manually.

- A volunteer's participations are not marked when they overlap with any of their leave.

Suggestion: Add a computed field similar to overlaps_holiday in volunteer.shift, to display on all views with participations. 

- For now, it is still possible for a volunteer to participate in a shift that over laps withtheir leave.

Suggestion: Add constraints and an error message if it is attempted.

