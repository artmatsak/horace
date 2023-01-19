from router import Router

backend = Router()

domain = {
    "business_name": "Death Star, a Star Wars-themed restaurant in Cupertino, CA",
    "extra_instructions": "In your speech, you impersonate Jedi Master Yoda."
}


@backend.command(desc="book a table", example_params=("Jose James", 2, "next Friday", "6:00 pm"))
def book_table(name: str, num_people: int, date: str, time: str) -> str:
    return "Booking successful, reference: YEHBZL"


@backend.command(desc="cancel a booking", example_params=("HTLYNN"))
def cancel_booking(reference: str) -> str:
    return "Booking canceled"
