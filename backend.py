import re
import random
import string
import logging
from router import Router
from datetime import datetime
from dateutil.relativedelta import relativedelta
import parsedatetime
from typing import Tuple, Dict, Any, Optional

backend = Router()

# Our booking "database" is a simple dict with some pre-populated entries
bookings = {
    "YBZ6HN": {
        "full_name": "Mary Ashcroft",
        "num_people": 5,
        "time": datetime(2023, 6, 2, 18, 15, 0)
    },
    "BZ2NLH": {
        "full_name": "James Jameson",
        "num_people": 2,
        "time": datetime(2023, 5, 22, 10, 30, 0)
    },
    "7BNZPN": {
        "full_name": "Julia Robbins",
        "num_people": 4,
        "time": datetime(2024, 1, 6, 19, 0, 0)
    }
}


# The @backend.command() decorator makes a Python function available to the
# chatbot as a backend command. For each command, you need to provide a short
# description and example parameters.
# Keep command and parameter names simple and descriptive to make it easier
# for the bot to "understand" what they do and how to use them.
@backend.command(desc="check if table is available for booking", example_params=(5, "tomorrow", "10:15 am"))
def check_table_availability(num_people: int, date: str, time: str) -> str:
    # Since our parameters will be coming from a language model, we can't take
    # chances and must validate them. At the very minimum, validation should
    # include casting of the parameters to the expected types.
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Checking table availability for ({repr(num_people)}, {repr(time)})")

    if not _is_table_available(num_people, time):
        return "No table available for the requested time"

    # The return value will be included in the prompt verbatim, as a backend
    # utterance. Use natural language to communicate the execution result to
    # the chatbot.
    return "The table is available"


@backend.command(desc="book a table", example_params=("Jose James", 2, "next Friday", "6:00 pm"))
def book_table(full_name: str, num_people: int, date: str, time: str) -> str:
    full_name = _validate_full_name(full_name)
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Booking table for ({repr(full_name)}, {repr(num_people)}, {repr(time)})")

    if not _is_table_available(num_people, time):
        return "No table available for the requested time"

    while True:
        reference = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(6))
        if reference not in bookings:
            break

    bookings[reference] = {
        "full_name": full_name,
        "num_people": num_people,
        "time": time
    }

    return "Booking confirmed: {}. Reference: {}".format(_format_booking(bookings[reference]), reference)


@backend.command(desc="get booking details", example_params=("YBNAPP",))
def get_booking_details(reference: str) -> str:
    reference = _validate_reference(reference)

    logging.debug(f"Getting booking details for ({repr(reference)},)")

    if reference not in bookings:
        return f"No such booking: {reference}"

    return "Found booking: {}".format(_format_booking(bookings[reference]))


@backend.command(desc="change booking", example_params=("ABGTBB", "Willy Tanner", 1, "May 4", "7:30 pm"))
def change_booking(reference: str, full_name: str, num_people: int, date: str, time: str) -> str:
    reference = _validate_reference(reference)
    full_name = _validate_full_name(full_name)
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Changing booking for ({repr(reference)}, {repr(full_name)}, {repr(num_people)}, {repr(time)})")

    if reference not in bookings:
        return f"No such booking: {reference}"
    elif not _is_table_available(num_people, time, ignore_reference=reference):
        return "No table available for the requested time"

    bookings[reference] = {
        "full_name": full_name,
        "num_people": num_people,
        "time": time
    }

    return "Booking {} changed: {}".format(reference, _format_booking(bookings[reference]))


@backend.command(desc="cancel a booking", example_params=("HTLYNN",))
def cancel_booking(reference: str) -> str:
    reference = _validate_reference(reference)

    logging.debug(f"Canceling booking for ({repr(reference)},)")

    if reference not in bookings:
        return f"No such booking: {reference}"

    del bookings[reference]

    return "Booking canceled"


def _validate_reference(reference: str) -> str:
    reference = str(reference)

    if not reference:
        raise ValueError("Reference is required")
    elif not re.fullmatch(r"[A-Z0-9]{6}", reference):
        raise ValueError(f"Invalid reference: {reference}. References consist"
                         "of 6 digits and/or uppercase letters")

    return reference


def _validate_full_name(full_name: str) -> str:
    full_name = str(full_name)

    if not full_name:
        raise ValueError("Full name is required")

    return full_name


def _validate_table_params(num_people: int, date: str, time: str) -> Tuple[int, datetime]:
    num_people = int(num_people)
    date = str(date)
    time = str(time)

    if num_people <= 0:
        raise ValueError("Number of people must be positive")
    elif num_people > 10:
        raise ValueError("Booking for more than 10 people is disallowed")
    elif not date:
        raise ValueError("Date is required")
    elif not time:
        raise ValueError("Time is required")

    cal = parsedatetime.Calendar()
    date_struct, _ = cal.parse(date)
    time_struct, _ = cal.parse(time)
    time = datetime(*(date_struct[:3] + time_struct[3:6]))

    if time < datetime.now():
        raise ValueError("Date and time cannot be in the past")
    elif time > datetime.now() + relativedelta(years=1):
        raise ValueError("Date and time cannot be more than a year from now")

    return num_people, time


def _is_table_available(
    num_people: int,
    time: datetime,
    ignore_reference: Optional[str] = None
) -> bool:
    # We only have one table at the restaurant and assume an average visit
    # duration of 2 hours
    previous_time = time - relativedelta(hours=2)
    next_time = time + relativedelta(hours=2)
    for reference, booking in bookings.items():
        if ignore_reference is not None and reference == ignore_reference:
            continue

        if previous_time < booking["time"] < next_time:
            return False

    return True


def _format_booking(booking: Dict[str, Any]) -> str:
    num_people_fmt = "1 person" if booking["num_people"] == 1 \
                     else f'{booking["num_people"]} people'
    time_fmt = booking["time"].strftime("%-I:%M %p on %B %-d, %Y")
    return "{}, {} at {}".format(booking["full_name"], num_people_fmt, time_fmt)
