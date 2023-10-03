"""
Бот повинен перебувати в безкінечному циклі, чекаючи команди користувача.
Бот завершує свою роботу, якщо зустрічає слова: .
Бот не чутливий до регістру введених команд.
Бот приймає команди:
"hello", відповідає у консоль "How can I help you?"
"add ...". За цією командою бот зберігає у пам'яті (у словнику наприклад) новий контакт. 
   Замість ... користувач вводить ім'я та номер телефону, обов'язково через пробіл.
"change ..." За цією командою бот зберігає в пам'яті новий номер телефону існуючого контакту. 
   Замість ... користувач вводить ім'я та номер телефону, обов'язково через пробіл.
"phone ...." За цією командою бот виводить у консоль номер телефону для зазначеного контакту. 
   Замість ... користувач вводить ім'я контакту, чий номер треба показати.
"show all". За цією командою бот виводить всі збереженні контакти з номерами телефонів у консоль.
"good bye", "close", "exit" по будь-якій з цих команд бот завершує свою роботу після того, 
   як виведе у консоль "Good bye!".
Всі помилки введення користувача повинні оброблятися за допомогою декоратора input_error. 
   Цей декоратор відповідає за повернення користувачеві повідомлень виду "Enter user name", 
   "Give me name and phone please" і т.п. 
   Декоратор input_error повинен обробляти винятки, що виникають у функціях-handler (KeyError, ValueError, IndexError)
   та повертати відповідну відповідь користувачеві.
Логіка команд реалізована в окремих функціях і ці функції приймають на вхід один або декілька рядків 
   та повертають рядок.
Вся логіка взаємодії з користувачем реалізована у функції main, всі print та input відбуваються тільки там.
"""

# У словнику будемо зберігати ім'я користувача як ключ і номер телефону як значення.
ADDRESSBOOK = {}

# Декоратор відповідає за повернення користувачеві повідомлень
def input_error(wrap):
    def inner(*args):
        try:
            return wrap(*args)
        except IndexError:
            return "Give me name and phone, please"
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Invalid input. Please provide name and phone number separated by space."
    return inner

# Функції обробники команд — набір функцій, які ще називають handler, 
# вони відповідають за безпосереднє виконання команд.
@input_error
def add_handler(data):  # Додавання нового контакту
    name = data[0].title()
    phone = data[1]
    ADDRESSBOOK[name] = phone
    return f"Contact {name} with phone {phone} was saved"

@input_error
def change_handler(data):  # Зміна номеру тедефону у існуючого конкакту
    name = data[0].title()
    phone = data[1]
    if name not in ADDRESSBOOK:
        raise KeyError
    ADDRESSBOOK[name] = phone
    return f"Phone number for contact {name} was changed to {phone}"

@input_error
def phone_handler(data):  # Вивод у консоль номера телефону зазначеного контакту
    name = data[0].title()
    if name not in ADDRESSBOOK:
        raise KeyError
    phone = ADDRESSBOOK[name]
    return f"The phone number for contact {name} is {phone}"

@input_error
def show_all_handler(*args):  # Вивод у консоль усіх контактів з номерами телефонів
    if not ADDRESSBOOK:
        return "The address book is empty"
    contacts = "\n".join([f"{name}: {phone}" for name, phone in ADDRESSBOOK.items()])
    return contacts

# Бот Починає свою роботу
def hello_handler(*args):
    return "How can I help you?"

# Бот завершує свою роботу
def exit_handler(*args):
    return "Good bye!"

# Парсер команд
def command_parser(raw_str: str):
    elements = raw_str.split()
    for func, cmd_list in COMMANDS.items():
        for cmd in cmd_list:
            if elements[0].lower() == cmd:
                return func, elements[1:]
    return None, None

# Команди
COMMANDS = {
    add_handler: ["add"],
    change_handler: ["change"],
    phone_handler: ["phone"],
    show_all_handler: ["show all"],
    exit_handler: ["good bye", "close", "exit"],
    hello_handler: ["hello"]
}

# Цикл запит-відповідь. Ця частина програми відповідає за отримання від користувача даних 
# та повернення користувачеві відповіді від функції-handlerа.
def main():
    while True:
        user_input = input(">>> ")
        if not user_input:
            continue
        func, data = command_parser(user_input)
        if not func:
            print("Unknown command. Type 'hello' for available commands.")
        else:
            result = func(data)
            print(result)
            if func == exit_handler:
                break

if __name__ == "__main__":
    main()
