from datetime import datetime
import pickle as pckl
import re
import os
from contextlib import suppress

from collections import UserDict
from datetime import datetime as dt



class Contact:
    def __init__(self, surname):
        self.surname = surname
        self.name = ''
        self._phones = []
        self._birthday = ''
        self._email = ''
        self.address = ''
        self.ui = None

    def add_name(self, name):
        if name:
            self.name = name

    def add_address(self, address):
        if address:
            self.address = address

    def update_surname(self, new_surname):
            self.surname = new_surname


    def update_phone(self, phones, *_):

        if phones and (phones[0] in self._phones):
            self._phones.remove(phones[0])
            self.phones = [phones[1]]            
    

    @property
    def phones(self):
        return self._phones

    @phones.setter
    def phones(self, phones: str):          
        if phones:
            for phone in phones:
                while True:            
                    san_phone = re.sub(r'[-)( ]', '', phone)            
                    if re.match(r'^(\+?\d{1,2}[- ]?)?\d{10,15}$', san_phone) or san_phone == '':
                        self._phones.append(san_phone)
                        break
                    else:
                        self.ui.show_red_message(f'This phone {phone} has invalid  format. Try again \033[0m [Enter to skip]')
                        phone = self.ui.user_input('Enter valid phone number [Enter to skip]:  ')

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email: str):
        if email:
            while True:                
                if re.match(r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$', email) or email == '':
                    self._email = email 
                    break
                else:
                    self.ui.show_red_message('Invalid email format. Try again\033[0m [Enter to skip]')
                    email = self.ui.user_input('Email [Enter to skip]:  ')

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, date_str):
        if date_str:
            while True:
                try:
                    parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                    if parsed_date.date() <= datetime.today().date():
                        self._birthday = date_str
                        break
                    else:
                        self.ui.show_red_message('The date cannot be in the future.\033[0m [Enter to skip]')
                except ValueError:
                    self.ui.show_red_message('Invalid Birthday format. Use -> dd.mm.yyyy\033[0m [Enter to skip]')
                date_str = self.ui.user_input(f'Birthday -> dd.mm.yyyy [Enter to skip]:  ')
                if not date_str:
                    break
    
    def __repr__(self) -> str:
        return '-' * 50 + f'\nSurname: {self.surname}\nName: {self.name}\nPhones: {", ".join(phone for phone in self.phones)}\nEmail: {self.email}\nBirthday: {self.birthday}\nAddress: {self.address}\n' + '-' * 50

    
def get_path(file_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))  
        return os.path.join(current_dir, f'../data/{file_name}')


class Iterator:
    def __init__(self):
        self.numbers_on_page = 5
        self.count_pages = 0
        self.n_page = 1
        self.idx = 0
        self.data_list = []
    
    def __iter__(self):
        return self
    
    def __next__(self):
        
        if self.n_page <= self.count_pages:
            page_list = []
            data_slice = self.data_list[self.idx:self.numbers_on_page*self.n_page]
            result = ''
            for key, record in data_slice:
                if data_slice.index((key, record)) == (len(data_slice) - 1):
                    self.n_page += 1
                page_list.append(record)
                self.idx += 1
            
            result = '\n'.join(str(p) for p in page_list)   
            return f'Page #{self.n_page - 1} from {self.count_pages}\n{result}'
        
        raise StopIteration

    def iterations(self, data_list, numbers_on_page=5, for_notes=False):
        try:
            self.numbers_on_page = int(numbers_on_page)
        except ValueError:
            pass
        
        if len(data_list)==0:
            return self
        
        count_pages = len(data_list)/self.numbers_on_page
        pages = int(count_pages)
        if count_pages > pages or pages == 0:
            self.count_pages = pages + 1
        else:
            self.count_pages = pages
        
        if for_notes:
            self.data_list = [(data_list.index(note), note) for note in data_list]
        else:
            self.data_list = [record for record in data_list.items()]
        self.idx = 0
        self.n_page = 1
        return self


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.notes = []
        self.note_id = 0
        self.iterator = Iterator()
        

    def add_contact(self, ui , contact: Contact):
            self.data.update({contact.surname:contact})
            contact.ui = ui
            ui.show_green_message('This command will guide you through creating new contact:\n')
            ui.show_message(f'Surname: {contact.surname}')
            contact.add_name(ui.user_input('Name [Enter to skip]: '))
            contact.phones = ui.user_input('Phones space-separate [Enter to skip]: ').split()
            contact.birthday = ui.user_input('Birthday -> dd.mm.yyyy [Enter to skip]: ')
            contact.email = ui.user_input('Email [Enter to skip]: ')
            contact.add_address(ui.user_input('Address [Enter to skip]: '))

    def update_contact(self, ui, contact: Contact):
        ui.show_green_message('This command will guide you through updating contact:\n')
        new_surname = ui.user_input(f'Surname: {contact.surname} [Enter to skip]: ') 
        if new_surname in self.data:
            ui.show_red_message(f'{new_surname} already exists ')
            return
        elif new_surname:
            self.data[new_surname] = contact
            del self.data[contact.surname]
            contact.update_surname(new_surname)      
        contact.ui = ui
        contact.add_name(ui.user_input(f'Name: {contact.name} [Enter to skip]: '))
        contact.update_phone(ui.user_input(f'{", ".join(contact.phones)} type old number and new number to replace [Enter to skip]: ').split())
        contact.birthday = ui.user_input(f'Birthday {contact.birthday} [Enter to skip]: ')
        contact.email = ui.user_input(f'Email: {contact.email} [Enter to skip]: ')
        contact.add_address(ui.user_input(f'Address: {contact.address} [Enter to skip]: '))

    def delete_contact(self, ui, contact: Contact):
        ui.show_red_message(f'Are you sure you want to delete the contact {contact.surname}?\n')
        if ui.user_input('Y/n:  ').lower() in ('y', 'yes'):
            del self.data[contact.surname]
            
    def nearby_birthday(self, ui, days):
        today = dt.now()
        nearby_contacts = []
        for contact in self.data.values():
            if contact.birthday:
                with suppress(ValueError):
                    birthdate = dt.strptime(contact.birthday, '%d.%m.%Y').replace(year=today.year)
                    days_until_birthday = (birthdate - today).days
                    if 0 <= days_until_birthday <= int(days):
                        nearby_contacts.append(contact)
        if nearby_contacts:
            for contact in nearby_contacts:
                ui.show_message(contact)
        else:
            ui.show_red_message("No contact with birthday within your date.")
            
    def show_contacts(self, ui, contacts_on_page=5):
        if not self.data:
            ui.show_message("AddressBook is empty")
        else:
            self.pagination(ui, self.iterator, self.data, contacts_on_page)
            
    def show_notes(self, ui, notes_on_page=5):
        if not self.notes:
            ui.show_message("List of Notes is empty")
        else:
            self.pagination(ui, self.iterator, self.notes, numbers_on_page=notes_on_page, for_notes=True)
            
    def pagination(self, ui, iterator: Iterator, data_list, numbers_on_page, for_notes=False):
        iterations = iterator.iterations(data_list, numbers_on_page=numbers_on_page, for_notes=for_notes)
        iter = 0
        for page in iterations:
            ui.show_message(page)
            iter += 1
            if iter < iterator.count_pages:
                if ui.user_input('            [Enter to next page]'):
                    break


    def delete_all(self, ui):
        if self.data:
            ui.show_red_message('Are you sure you want to clear the AddressBook?\n')
            if ui.user_input('Y/n:  ').lower() in ('y', 'yes'):
                self.data.clear()
                ui.show_green_message('The AddressBook is empty!')
        else:
            ui.show_green_message('The AddressBook is empty!')
        
        if len(self.notes):
            ui.show_red_message('Are you sure you want to clear the Notes?\n')
            if ui.user_input('Y/n:  ').lower() in ('y', 'yes'):
                self.notes.clear()
                ui.show_green_message('The Notes list is empty!')
        else:
            ui.show_green_message('The Notes list is empty!')
            

    def log(self, action):
        time = dt.strftime(dt.now(), '%H:%M:%S')
        msg = f'[{time} {action}]'
        with open(get_path("logs.txt"), "a+") as file:
            file.write(f'{msg}\n')

    def save(self):
        with open(get_path("auto_save.bin"), "wb") as file:
            pckl.dump(self.data, file)
        self.log(f'AddressBook saved')
        with open(get_path("notes.bin"), "wb") as file:
            pckl.dump(self.notes, file)
        self.log(f'Notes saved')

    def load(self):
        with suppress(FileNotFoundError):
            with open(get_path("auto_save.bin"), "rb") as file:
                self.data = pckl.load(file)
        self.log(f'AddressBook loaded')
        with suppress(FileNotFoundError):
            with open(get_path("notes.bin"), "rb") as file:
                self.notes = pckl.load(file)
                if self.notes:
                    self.note_id = int(self.notes[-1].id.split()[0])
        self.log(f'Notes loaded')
        return self.data, self.notes
