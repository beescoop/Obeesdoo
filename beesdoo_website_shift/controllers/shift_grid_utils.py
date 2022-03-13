# Copyright 2017-2020 Coop IT Easy SCRLfs (http://coopiteasy.be)
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import namedtuple
from datetime import date, datetime, timedelta
from itertools import groupby
from typing import Dict, Iterable, List, Tuple

import pytz

from odoo.http import request

# Model used in the templates. Behaves like a tuple
# but also allows accessing elements by name
DisplayedShift = namedtuple(
    "DisplayedShift",
    ["shift", "free_space", "is_subscribed", "has_enough_workers"],
)


def _localize(timestamp: datetime) -> datetime:
    tz_name = request.env.user.tz or pytz.utc.zone
    utc_timestamp = pytz.utc.localize(timestamp, is_dst=False)  # UTC = no DST
    context_tz = pytz.timezone(tz_name)
    return utc_timestamp.astimezone(context_tz)


def _start_end_tuple(ds: DisplayedShift) -> Tuple[str, str]:
    local_start = _localize(ds.shift.start_time)
    local_end = _localize(ds.shift.end_time)
    return local_start.strftime("%H:%M"), local_end.strftime("%H:%M")


def _group_by_day(shifts: Iterable[DisplayedShift], monday: date) -> List:
    groupby_iter = groupby(shifts, key=lambda ds: ds.shift.start_time.date())
    shifts_by_day = {
        # fixme can we have several shifts per time/date here? I'd say yes
        day: list(grouped_shifts)
        for day, grouped_shifts in groupby_iter
    }

    # fill the gaps
    weekdays = (monday + timedelta(days=i) for i in range(7))
    return [shifts_by_day.get(day, None) for day in weekdays]


def _group_by_time(shifts: Iterable[DisplayedShift], monday: date) -> Dict:
    groupby_iter = groupby(sorted(shifts, key=_start_end_tuple), key=_start_end_tuple)
    shifts_by_time = [
        ((start, end), _group_by_day(grouped_shifts, monday))
        for (start, end), grouped_shifts in groupby_iter
    ]
    headers = [monday + timedelta(days=i) for i in range(7)]
    return {"headers": headers, "rows": shifts_by_time}


def _get_previous_monday(dshift: DisplayedShift) -> DisplayedShift:
    start_time = dshift.shift.start_time.date()
    return start_time + timedelta(days=-start_time.weekday())


def build_shift_grid(shifts: List[DisplayedShift]) -> List:
    """
    Takes a list of shifts as arguments and builds a grid
    to be displayed by available_shift_irregular_worker_grid.
    The output looks like:
    [(datetime.date(2021, 1, 18),  # week
        {'headers': [datetime.date(2021, 1, 18), ]  # week days
         'rows': [(('07:00', '09:15'),  # start and end time
                   [DisplayedShift(  # shifts by day or None (7 columns)
                        shift=beesdoo.shift.shift(11950,),
                        free_space=1,
                        is_subscribed=False,
                        has_enough_workers=False)), *
                    ], *
                  ), ...
                 ],
        }), ...
    """
    # groupby only works on sorted sets.
    groupby_iter = groupby(
        sorted(shifts, key=_get_previous_monday), key=_get_previous_monday
    )
    shifts_by_week = [
        (monday, _group_by_time(grouped_shifts, monday))
        for monday, grouped_shifts in groupby_iter
    ]
    return sorted(shifts_by_week, key=lambda t: t[0])
