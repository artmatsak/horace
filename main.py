from router import Router


backend = Router()


@backend.command(desc="book a table", example_params=(2, "2023-03-04 6:00 pm"))
def book_table(num_people: int, datetime: str) -> str:
    return "Booking successful, reference: YEHBZL"


if __name__ == '__main__':
    print(backend.registry)

    try:
        command_json = '{"command": "book_table", "params": {"num_people": 2, "datetime": "2023-03-04 6:00 pm"}}'
        print(backend.invoke(command_json))
    except Exception as e:
        print(e)
