import re
import random
import string
import logging
from router import Router
from datetime import datetime
from dateutil.relativedelta import relativedelta
import parsedatetime
from typing import Tuple

backend = Router()

bookings = {
    "YBZ6HN": {
        "name": "Mary Ashcroft",
        "num_people": 5,
        "time": datetime(2023, 6, 2, 18, 15, 0)
    },
    "BZ2NLH": {
        "name": "James Jameson",
        "num_people": 2,
        "time": datetime(2023, 5, 22, 10, 30, 0)
    },
    "7BNZPN": {
        "name": "Julia Robbins",
        "num_people": 4,
        "time": datetime(2024, 1, 6, 19, 0, 0)
    }
}


@backend.command(desc="check if table is available for booking", example_params=(5, "tomorrow", "10:15 am"))
def check_table_availability(num_people: int, date: str, time: str) -> str:
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Checking table availability for ({repr(num_people)}, {repr(time)})")

    if not _is_table_available(num_people, time):
        return "The table is not available"

    return "The table is available"


@backend.command(desc="book a table", example_params=("Jose James", 2, "next Friday", "6:00 pm"))
def book_table(name: str, num_people: int, date: str, time: str) -> str:
    name = _validate_name(name)
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Booking table for ({repr(name)}, {repr(num_people)}, {repr(time)})")

    if not _is_table_available(num_people, time):
        return "The table is not available"

    while True:
        reference = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(6))
        if reference not in bookings:
            break

    bookings[reference] = {
        "name": name,
        "num_people": num_people,
        "time": time
    }

    return f"Booking confirmed, reference: {reference}"


@backend.command(desc="get booking details", example_params=("YBNAPP",))
def get_booking_details(reference: str) -> str:
    reference = _validate_reference(reference)

    logging.debug(f"Getting booking details for ({repr(reference)},)")

    if reference not in bookings:
        return f"No such booking: {reference}"

    booking = bookings[reference]
    num_people_fmt = "1 person" if booking["num_people"] == 1 \
                     else f'{booking["num_people"]} people'
    time_fmt = booking["time"].strftime("%-I:%M %p on %B %-d, %Y")

    return "Found booking for {}, {} at {}".format(booking["name"], num_people_fmt, time_fmt)


@backend.command(desc="change booking", example_params=("ABGTBB", "Willy Tanner", 1, "May 4", "7:30 pm"))
def change_booking(reference: str, name: str, num_people: int, date: str, time: str) -> str:
    reference = _validate_reference(reference)
    name = _validate_name(name)
    num_people, time = _validate_table_params(num_people, date, time)

    logging.debug(
        f"Changing booking for ({repr(reference)}, {repr(name)}, {repr(num_people)}, {repr(time)})")

    if reference not in bookings:
        return f"No such booking: {reference}"

    bookings[reference] = {
        "name": name,
        "num_people": num_people,
        "time": time
    }

    return f"Booking {reference} changed"


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


def _validate_name(name: str) -> str:
    name = str(name)

    if not name:
        raise ValueError("Name is required")

    return name


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


def _is_table_available(num_people: int, time: datetime) -> bool:
    # We only have one table at the restaurant and assume an average visit
    # duration of 2 hours
    previous_time = time - relativedelta(hours=2)
    next_time = time + relativedelta(hours=2)
    for booking in bookings.values():
        if previous_time < booking["time"] < next_time:
            return False

    return True
