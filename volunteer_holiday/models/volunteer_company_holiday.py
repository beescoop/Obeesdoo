# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class VolunteerCompanyHoliday(models.Model):
    _name = "volunteer.company.holiday"
    _description = "Company Holidays"
    _order = "start_date"

    # Fields

    name = fields.Char(required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    start_date = fields.Date(required=True)

    end_date = fields.Date(required=True)

    # Methods

    # Retirer la limite de temps, regarder les shifts futurs
    def _cancel_holiday_shift(self, time_in_months=3):
        """Cancel shifts if they cover holiday period within time range."""
        today_midnight = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Setting the time range we want to work with, here 3 months
        date_time_range = today_midnight + relativedelta(months=time_in_months)

        confirmed_future_generated_shifts_in_range = (
            self.env["volunteer.shift"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    ("start_time", ">=", today_midnight),
                    ("start_time", "<=", date_time_range),
                    ("generator_id", "!=", None),
                    ("generator_id.is_maintained_during_holiday", "=", False),
                ]
            )
        )

        future_company_holidays_in_range = (
            self.env["volunteer.company.holiday"]
            .sudo()
            .search(
                [
                    ("start_date", ">=", today_midnight),
                    ("start_date", "<=", date_time_range.date()),
                ]
            )
        )

        # Create dictionary key-company for list of values-shifts
        shifts_by_company = {}
        for shift in confirmed_future_generated_shifts_in_range:
            shifts_by_company.setdefault(shift.company_id, []).append(shift)

        for holiday in future_company_holidays_in_range:
            same_company_shifts = shifts_by_company.get(holiday.company_id, [])
            for shift in same_company_shifts:
                if shift.state != "canceled" and self._shift_covers_holiday(
                    shift.start_time,
                    shift.end_time,
                    holiday.start_date,
                    holiday.end_date,
                ):
                    shift.sudo().write(
                        {
                            "stage_id": self.env.ref(
                                "volunteer.volunteer_shift_stage_canceled"
                            ).id
                        }
                    )

    @api.model
    def _shift_covers_holiday(
        self, shift_start_time, shift_end_time, holiday_start_date, holiday_end_date
    ):
        """Compare two periods of time, return true if they overlap."""
        shift_start_date = shift_start_time.date()
        shift_end_date = shift_end_time.date()

        return (
            (
                shift_start_date >= holiday_start_date
                and shift_start_date <= holiday_end_date
            )
            or (
                shift_end_date >= holiday_start_date
                and shift_start_date <= holiday_end_date
            )
            or (
                shift_start_date <= holiday_start_date
                and shift_end_date >= holiday_end_date
            )
        )

    # Override Methods : DRAFT ! il faut encore préciser des conditions qui
    # vérifieront que ça vaut la peine de lancer la fonction (qu'il y a bien
    # des shifts à annuler dans l'interval de temps entre les anciennes dates
    # de début et de fin des vacances).

    # def write(self, vals):
    #     if "start_date" in vals or "end_date" in vals:
    #         canceled_shifts_during_holiday = self.env["volunteer_shift"].sudo().search(
    #             [
    #                 ("shift.state", "=", "canceled"),
    #                 ("shift.generator_id", "!=", None),
    #                 ("shift.generator_id.is_maintained_during_holiday", "=", False),
    #                 # the 2 last domains could be replaced by one if we add the bool
    #                 # is_canceled_by_holiday
    #             ]
    #         )
    #         for holiday in self:
    #             old_start_date = holiday.start_date
    #             old_end_date = holiday.end_date
    #             shifts_to_uncancel = []
    #             if vals["start_date"] > old_start_date:
    #                 temp_shifts_to_uncancel = canceled_shifts_during_holiday.filtered(
    #                     lambda shift: shift.start_time.date() > old_start_date
    #                     and shift.start_time.date() < vals["start_date"]
    #                 )
    #                 shifts_to_uncancel.extend(temp_shifts_to_uncancel)
    #             elif vals["end_date"] < old_end_date:
    #                 temp_shifts_to_uncancel = canceled_shifts_during_holiday.filtered(
    #                     lambda shift: shift.end_time.date() < old_end_date
    #                     and shift.end_time.date() > vals["end_date"]
    #                 )
    #                 shifts_to_uncancel.extend(temp_shifts_to_uncancel)
    #             for shift in shifts_to_uncancel:
    #                 shift.write(
    #                     {
    #                         "stage_id": self.env.ref(
    #                             "volunteer.volunteer_shift_stage_confirmed"
    #                         ).id
    #                     }
    #                 )
    # TODO: Aussi penser aux participations de chaque shift,
    # si on les repasse en confirmé, lesquelles, etc
    #     super().write(vals)
