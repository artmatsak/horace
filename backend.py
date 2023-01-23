from router import Router
from datetime import datetime
from dateutil.relativedelta import relativedelta
import parsedatetime
from typing import Tuple

backend = Router()


@backend.command(desc="check if table is available for booking", example_params=(5, "tomorrow", "10:15 am"))
def check_table_availability(num_people: int, date: str, time: str) -> str:
    num_people, time = _validate_table_params(num_people, date, time)
    return "The table is available"


@backend.command(desc="book a table", example_params=("Jose James", 2, "next Friday", "6:00 pm"))
def book_table(name: str, num_people: int, date: str, time: str) -> str:
    name = _validate_name(name)
    num_people, time = _validate_table_params(num_people, date, time)
    return "Booking confirmed, reference: YEHBZL"


@backend.command(desc="get booking details", example_params=("YBNAPP",))
def get_booking_details(reference: str) -> str:
    return "Found booking for May Longhorn, 4 people at 8:30 pm on August 3, 2023"


@backend.command(desc="change booking", example_params=("ABGTBB", "Willy Tanner", 1, "May 4", "7:30 pm"))
def change_booking(reference: str, name: str, num_people: int, date: str, time: str) -> str:
    name = _validate_name(name)
    num_people, time = _validate_table_params(num_people, date, time)
    return f"Booking {reference} changed"


@backend.command(desc="cancel a booking", example_params=("HTLYNN",))
def cancel_booking(reference: str) -> str:
    return "Booking canceled"


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
