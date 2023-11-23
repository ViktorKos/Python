import os


    

class ConsoleUserInterface():
    help_message = """
                        \033[92m List of all commands:
  'add', '+' [\033[90msurname\033[92m]      - adding a new contact to the Address Book
  'add notes', 'add notes ' - adding a new note to Notes
  'change' [\033[90msurname\033[92m]        - changing an existing contact
  'change note' [\033[90mnote id\033[92m]   - changing an existing note
  'find' [\033[90manything\033[92m]         - searching for contacts by the entered text in a property value
  'delete note' [\033[90mnote id\033[92m]   - delete a note from Notes 
  'del', 'delete', 'remove' [\033[90msurname\033[92m]     - delete a contact from the Address Book
  'delete all', 'remove all', 'clean'     - complete cleaning of the Address Book
  'show all', 'show', 'pages' 'contacts'  - display of all contacts in the address book
  'show notes', 'notes'                   - display of all Notes in the Address Book
  'sort' [\033[90mpath\033[92m]                           - sorting files in directories
  'exit', 'quit', 'goodbye',  '.'         - completion of work with the address book, automatic saving of changes made
  'find tag' [\033[90mtag\033[92m]                        - searching for notes by the entered tag \033[0m
"""

    
    @staticmethod
    def show_green_message(text):
        print(f'\033[92m{text}\033[0m', end="\n")
    
    @staticmethod
    def show_red_message(text):
        print(f'\033[91m{text}\033[0m', end="\n")
    
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def user_input(self, message=''):
        answer = input(message)
        return answer
    
    def show_message(self, message):
        print(message)

    def show_help(self):
        print(self.help_message)

    def show_start_message(self):
        ConsoleUserInterface.clear_screen()
        hello_message = '''                 "PROGRAMMULINKA"
        What's up buddy!
        I will be your assistant!'''
        ConsoleUserInterface.show_green_message(hello_message)
        
