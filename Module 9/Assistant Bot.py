# decorator for input validation
def input_error(func):
    def inner(userData: tuple, USER_DATA: dict):
        response = ""
        if func.__name__ == "add_phone_handler" \
                or func.__name__ == "change_phone_handler":
            if userData[0] == "" or userData[1] == "":
                response = "Provide user name and phone number.\n"
        elif func.__name__ == "show_phone_handler":
            if userData[0] == "":  # name is empty
                response = "Provide user name.\n"
        if response == "":
            try:
                response = func(userData, USER_DATA)  # call decorated function
            except KeyError:
                response = "Error: cannot find this user."
            except ValueError:
                response = "Error: cannot handle phone number."
            except IndexError:
                response = "Error: dictionary index error."
            except:
                response = "Error: unclassified error occured."
        return response
    return inner


def hello_handler(isWorking: bool):
    if isWorking:
        responseMessage = "Already working. Please enter an action command.\n"
    else:
        responseMessage = "How can I help you?\n"
    return responseMessage


def exit_handler():
    responseMessage = "Good bye!"
    return responseMessage


@input_error
def add_phone_handler(userData: tuple, USER_DATA: dict):
    if userData[0] in USER_DATA:
        responseMessage = f"Record for {userData[0]} already exists."
    else:
        USER_DATA[userData[0]] = userData[1]
        responseMessage = "Record was added.\n"
    return responseMessage


@input_error
def change_phone_handler(userData: tuple, USER_DATA: dict):
    if userData[0] in USER_DATA.keys():
        USER_DATA[userData[0]] = userData[1]
    else:
        raise KeyError
    responseMessage = "Record was changed.\n"
    return responseMessage


@input_error
def show_phone_handler(userData: tuple, USER_DATA: dict):
    userPhoneNumber = USER_DATA[userData[0]]
    responseMessage = f"Found {userData[0]}: {userPhoneNumber}.\n"
    return responseMessage


@input_error
def show_all_phones_handler(userData: tuple, USER_DATA):
    if USER_DATA:
        responseMessage = "Current dictionary contains:\n"
        for item in enumerate(USER_DATA.items(), 1):
            responseMessage += f"{item[0]}. {item[1][0]}: {item[1][1]}\n"
    else:
        responseMessage = "Current dictionary is empty.\n"
    return responseMessage


# decorator for command validation

def get_command_handler(command: str, COMMAND_HANDLER: dict):
    command = command.lower()
    commandHandler = None
    if COMMAND_HANDLER:
        commandHandler = COMMAND_HANDLER.get(command)
    return commandHandler

# parse user input


def parse_command_line(command_line: str, COMMAND: dict) -> str:
    command = ""
    userPhoneNumber = ""
    userName = ""
    userData = []
    for registeredCommand in COMMAND:
        if command_line.startswith(registeredCommand):
            command = registeredCommand
            data = command_line.removeprefix(command).strip()
            if data:
                data_components = data.split(" ")
                for component in data_components:
                    if component.isalpha():
                        userName += component + " "
                userName = userName.strip()
                userPhoneNumber = data.removeprefix(userName).strip()
            break
    userData.append(userName)
    userData.append(userPhoneNumber)
    return (command, userData)


def main():
    USER_DATA = {
        "": "",
    }

    isWorking = False

    COMMAND = {
        "hello": "Start work with this bot",
        "add": "Add a phone number - add <user name> <phone number>",
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

    commandHandler = None
    print("Hello! This is assistant bot. Here is what I can do:")
    for key, value in COMMAND.items():
        print("{:<15}{}".format(key, value))

    # awaiting for a command to start the bot or exit
    while not isWorking:
        inputCommand = str(
            input("Please enter a command to start work or exit:\n"))
        parsedCommand = parse_command_line(inputCommand, COMMAND)
        commandHandler = get_command_handler(parsedCommand[0], COMMAND_HANDLER)
        if not commandHandler is None:
            if commandHandler.__name__ == "hello_handler":
                response = commandHandler(isWorking)
                print(response)
                isWorking = True
                USER_DATA.clear()
            elif commandHandler.__name__ == "exit_handler":
                response = commandHandler()
                print(response)
                break
            else:
                print(
                    f"Cannot start work with action command {parsedCommand[0]}.\n")
        else:
            print("The command does not exist.\n")
    # work loop
    while isWorking:
        inputCommand = str(input("Please enter an action command:\n"))
        # parse input, get a command and userData
        parsedCommand = parse_command_line(inputCommand, COMMAND)
        commandHandler = get_command_handler(
            parsedCommand[0], COMMAND_HANDLER)  # command
        if not commandHandler is None:
            if commandHandler.__name__ == "hello_handler":
                response = commandHandler(isWorking)
                print(response)
            elif commandHandler.__name__ == "exit_handler":
                response = commandHandler()
                print(response)
                isWorking = False
            else:
                response = commandHandler(
                    parsedCommand[1], USER_DATA)  # userData
                print(response)
        else:
            print(f"The command {parsedCommand[0]} does not exist.")
    return


if __name__ == "__main__":
    main()