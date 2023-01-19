from router import Router
from datetime import datetime
from dateutil.relativedelta import relativedelta
import parsedatetime

backend = Router()

domain = {
    "business_name": "Death Star, a Star Wars-themed restaurant in Cupertino, CA",
    "extra_instructions": "In your speech, you impersonate Jedi Master Yoda."
}


@backend.command(desc="book a table", example_params=("Jose James", 2, "next Friday", "6:00 pm"))
def book_table(name: str, num_people: int, date: str, time: str) -> str:
    name = str(name)
    num_people = int(num_people)
    date = str(date)
    time = str(time)

    if not name:
        raise ValueError("Name is required")
    elif num_people <= 0:
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

    return f"Booking confirmed, reference: YEHBZL"


@backend.command(desc="cancel a booking", example_params=("HTLYNN"))
def cancel_booking(reference: str) -> str:
    return "Booking canceled"
