from calendar import isleap
from collections import UserDict
from datetime import date, datetime
import re


class SingltonException(Exception):
    def __init__(self, obj_type: str) -> None:
        self.obj_type = obj_type
        super().__init__(f"Field of this type: {obj_type} already exists")


class NoFieldTypeException(Exception):
    def __init__(self, obj_type: str) -> None:
        self.obj_type = obj_type
        super().__init__(f"Field of this type: {obj_type} does not exist")


class Field():
    def __init__(self, value, is_singlton: bool = None) -> None:
        self.value = value
        self.is_singlton = is_singlton if is_singlton else False


class Name(Field):
    def __init__(self, name: str) -> None:
        self.__value = None
        super().__init__(name, is_singlton=True)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if new_value == "":
            raise ValueError("Name cannot be empty.")
        self.__value = new_value


class Phone(Field):
    def __init__(self, phone_number: str) -> None:
        self.__value = None
        super().__init__(phone_number)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        phone = re.findall(
            r"^(?:\+3{0,1}8)?(?:\({0,1}0[0-9]{2}\){0,1}[0-9]{7})$", new_value
        )
        if phone:
            self.__value = new_value
        else:
            raise ValueError(
                "Provided value is not recognized as phone number.")


class Birthday(Field):
    def __init__(self, birthday: date) -> None:
        self.__value = None
        super().__init__(birthday, is_singlton=True)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        try:
            date_value = datetime.date(
                datetime.strptime(new_value, "%d.%m.%Y"))
        except:
            raise ValueError("Date expected as dd.mm.yyyy.")
        if date_value > datetime.date(datetime.now()):
            raise ValueError("Birthday must be date in past.")
        else:
            self.__value = date_value


class Record():

    next_free_id = 1

    def __init__(
        self, user_name: Name,
        phone_number: Phone = None,
        birthday: Birthday = None
    ) -> None:

        self.ID = Record.next_free_id
        Record.next_free_id += 1
        self.user_name = user_name
        self.fields = []
        if phone_number:
            self.add_field(phone_number)
        if birthday:
            self.add_field(birthday)

    def edit_user_name(self, user_name_value: str) -> None:
        self.user_name.value = user_name_value

    def find_field(self, field_obj: Field) -> Field:
        fields = list(
            filter(lambda field: field == field_obj, self.fields))
        return fields[0] if fields else None

    def add_field(self, field_obj: Field) -> None:
        if field_obj.is_singlton:
            fields = list(
                filter(lambda field: type(field) ==
                       type(field_obj), self.fields)
            )
            if fields:
                raise SingltonException(type(field_obj))
            else:
                self.fields.append(field_obj)
        elif self.find_field(field_obj) is None:
            self.fields.append(field_obj)

    def delete_field(self, field_obj: Field) -> None:
        if self.find_field(field_obj) is not None:
            self.fields.remove(field_obj)

    def edit_field(self, oldfield_obj: Field, newfield_obj: Field) -> None:
        field = self.find_field(oldfield_obj)
        if field is not None:
            i = self.fields.index(field)
            self.fields[i] = newfield_obj

    def days_to_birthday(self) -> int:
        next_birthday = None
        fields = list(
            filter(lambda field: isinstance(field, Birthday), self.fields)
        )
        if not fields:
            raise NoFieldTypeException(type(Birthday))
        else:
            birthday = fields[0].value  # date
            Feb29_birthdate = False
            if birthday.month == 2 and birthday.day == 29 \
                    and not isleap(datetime.now().year):
                Feb29_birthdate = True
                birthday_this_year = date(datetime.now().year, 2, 28)
            else:
                birthday_this_year = date(
                    datetime.now().year,
                    birthday.month,
                    birthday.day
                )
            # if the birthday this year already occurred take the next year
            if birthday_this_year < datetime.date(datetime.now()):
                next_birthday = birthday_this_year.replace(
                    year=birthday_this_year.year+1)
                if Feb29_birthdate and isleap(next_birthday.year):
                    next_birthday = birthday_this_year.replace(
                        day=birthday_this_year.day+1)
            else:
                next_birthday = birthday_this_year
        return (next_birthday - datetime.date(datetime.now())).days


class Address_Book(UserDict):

    def __init__(self, address_bookName: str) -> None:
        self.name = address_bookName
        self.recordsCount = 0
        super().__init__()

    def find_record(self, user_name: str) -> Record:
        records = []
        if self.recordsCount > 0:
            records = list(
                filter(lambda record_name: record_name == user_name, self.data))
        # records[0] contains a key of found record, if any.
        return self.data[records[0]] if records else None

    def add_record(self, record: Record) -> None:
        user_name = record.user_name.value
        existingRecord = self.find_record(user_name)
        if existingRecord is None:
            self.data[user_name] = record
            self.recordsCount += 1

    def delete_record(self, user_name: str) -> None:
        if self.recordsCount > 0:
            existingRecord = self.find_record(user_name)
            if existingRecord is not None:
                deletedRecord = self.data.pop(user_name)
                self.recordsCount -= 1

    def iterator(self, page_size: int = 5):
        records_pool = [self.data[key] for key in self.data]
        page_start_index = 0
        while page_start_index < len(records_pool):
            try:
                yield records_pool[page_start_index: page_start_index+page_size]
                page_start_index += page_size
            except:
                break

# decorator for input validation


def input_error(func):
    def inner(user_data: tuple, address_book: Address_Book):
        response = ""
        if func.__name__ == "add_phone_handler" \
                or func.__name__ == "change_phone_handler":
            if user_data[0] == "" or user_data[1] == "":
                response = "Provide user name and phone number.\n"
        elif func.__name__ == "show_phone_handler":
            if user_data[0] == "":  # name is empty
                response = "Provide user name.\n"
        if response == "":
            try:
                # call decorated function
                response = func(user_data, address_book)
            except KeyError:
                response = "Error: cannot find this user."
            except ValueError:
                response = "Error: cannot handle record value."
            except IndexError:
                response = "Error: dictionary index error."
            except Exception as e:
                response = f"Error: {e.args[0]}"
        return response
    return inner


def hello_handler(is_working: bool):
    if is_working:
        responseMessage = "Already working. Please enter an action command.\n"
    else:
        responseMessage = "How can I help you?\n"
    return responseMessage


def exit_handler():
    responseMessage = "Good bye!"
    return responseMessage


@ input_error
def add_phone_handler(user_data: tuple, address_book: Address_Book):
    user_name = user_data[0]
    phone = Phone(user_data[1]) if user_data[1] != "" else None
    birthday = Birthday(user_data[2]) if user_data[2] != "" else None
    record = address_book.find_record(user_name)
    if record is None:
        newRecord = Record(Name(user_name), phone, birthday)
        address_book.add_record(newRecord)
        responseMessage = "Record was added.\n"
    else:
        # create an updated record
        record.add_field(phone)
        if birthday:
            record.add_field(birthday)
        address_book[user_name] = record
        responseMessage = f"Record for {user_name} was updated.\n"
    return responseMessage


@ input_error
def change_phone_handler(user_data: tuple, address_book: Address_Book):
    user_name = user_data[0]
    phone = Phone(user_data[1])
    record = address_book.find_record(user_name)
    if record is not None:
        currentValue = record.find_field(phone)
        if currentValue is not None:
            # logic of input should be changed as multiple numbers allowed
            # here current value should be replaced with new value, which needs to be added to user_data
            record.edit_field(currentValue, currentValue)
        else:
            raise ValueError
    else:
        raise KeyError
    responseMessage = "Record  was changed.\n"
    return responseMessage


@ input_error
def show_phone_handler(user_data: tuple, address_book: Address_Book):
    user_name = user_data[0]
    record = address_book.find_record(user_name)
    if record is not None:
        phones = [
            field.value for field in record.fields if isinstance(field, Phone)
        ]
        # get birthday date and days to the next one
        try:
            days = record.days_to_birthday()
        except NoFieldTypeException:
            days = None
        else:
            birthday = [
                field.value for field in record.fields if isinstance(field, Birthday)
            ]
        if days:
            responseMessage = f"Found {user_name} ({birthday[0]}, {days} days to next birthday): {', '.join(phones)}.\n"
        else:
            responseMessage = f"Found {user_name}: {', '.join(phones)}.\n"
    else:
        responseMessage = f"Not found: {user_name}.\n"
    return responseMessage


@input_error
def show_all_phones_handler(user_data: tuple, address_book: Address_Book):
    if address_book.recordsCount > 0:
        responseMessage = "Current address book contains:\n"
        page_size = 2
        start_position = 1
        for book in address_book.iterator(page_size):
            for item in enumerate(book, start_position):
                position = item[0]
                user_name = item[1].user_name.value
                phones = ", ".join(
                    [field.value for field in item[1].fields if isinstance(field, Phone)])
                responseMessage += f"{position}. {user_name}: {phones}\n"
            start_position += page_size
    else:
        responseMessage = "Current address book is empty.\n"
    return responseMessage


# decorator for a command validation

def get_command_handler(command: str, COMMAND_HANDLER: dict):
    command = command.lower()
    command_handler = None
    if COMMAND_HANDLER:
        command_handler = COMMAND_HANDLER.get(command)
    return command_handler


# parse user input

def parse_command_line(command_line: str, COMMAND: dict) -> str:
    command = ""
    userphone_number = ""
    user_name = ""
    user_birthday = ""
    user_data = []
    for registeredCommand in COMMAND:
        if command_line.startswith(registeredCommand):
            command = registeredCommand
            data = command_line.removeprefix(command).strip()
            if data:
                data_components = data.split(" ")
                for component in data_components:
                    if component.isalpha():
                        user_name += component + " "
                user_name = user_name.strip()
                data_components = data.removeprefix(user_name).strip()
                data = data_components.split()
                if data:
                    userphone_number = data[0] if data[0] else ""
                    try:
                        user_birthday = data[1] if data[1] else ""
                    except:
                        user_birthday = ""
            break
    user_data.append(user_name)
    user_data.append(userphone_number)
    user_data.append(user_birthday)
    return (command, user_data)


def main():

    is_working = False

    COMMAND = {
        "hello": "Start work with this bot",
        "add": "Add a phone number - add <user name> <phone number> [birthday]",
        "change": "Change a phone number - change <user name> <phone number>",
        "phone": "Show user's phone number - phone <user name>",
        "show all": "Show all contacts",
        "good bye": "Finish work and exit",
        "close": "Finish work and exit",
        "exit": "Finish work and exit"
    }

    COMMAND_HANDLER = {
        "hello": hello_handler,
        "add": add_phone_handler,
        "change": change_phone_handler,
        "phone": show_phone_handler,
        "show all": show_all_phones_handler,
        "good bye": exit_handler,
        "close": exit_handler,
        "exit": exit_handler
    }

    command_handler = None
    print("Hello! This is assistant bot. Here is what I can do:")
    for key, value in COMMAND.items():
        print("{:<15}{}".format(key, value))

    # awaiting for a command to start the bot or exit
    while not is_working:
        input_command = str(
            input("Please enter a command to start work or exit:\n"))
        parsed_command = parse_command_line(input_command, COMMAND)
        command_handler = get_command_handler(
            parsed_command[0], COMMAND_HANDLER)
        if command_handler is not None:
            if command_handler.__name__ == "hello_handler":
                response = command_handler(is_working)
                print(response)
                is_working = True
                address_book = Address_Book("General")
            elif command_handler.__name__ == "exit_handler":
                response = command_handler()
                print(response)
                break
            else:
                print(
                    f"Cannot start work with action command {parsed_command[0]}.\n")
        else:
            print("The command does not exist.\n")
    # work loop
    while is_working:
        input_command = input("Please enter an action command:\n")
        # parse input, get a command and user_data
        parsed_command = parse_command_line(input_command, COMMAND)
        command_handler = get_command_handler(
            parsed_command[0], COMMAND_HANDLER)  # command
        if command_handler is not None:
            if command_handler.__name__ == "hello_handler":
                response = command_handler(is_working)
                print(response)
            elif command_handler.__name__ == "exit_handler":
                response = command_handler()
                print(response)
                is_working = False
            else:
                response = command_handler(
                    parsed_command[1], address_book)  # user_data
                print(response)
        else:
            print(f"The command {parsed_command[0]} does not exist.")
    return


if __name__ == "__main__":
    main()
