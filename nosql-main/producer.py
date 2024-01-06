import json
import faker
from mongoengine import connect, Document, StringField, BooleanField
import pika

class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(default=False)

def create_fake_contacts(num_contacts):
    fake = faker.Faker()
    contacts = []
    for _ in range(num_contacts):
        contact = Contact(
            fullname=fake.name(),
            email=fake.email(),
        )
        contacts.append(contact)
    return contacts

def save_contacts_to_db(contacts):
    for contact in contacts:
        contact.save()

def send_contact_to_queue(contact):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='contacts_queue')

    message = {'contact_id': str(contact.id)}
    channel.basic_publish(exchange='', routing_key='contacts_queue', body=json.dumps(message))

    print(f"Contact {contact.id} sent to the queue")

    connection.close()

if __name__ == "__main__":
    connect('contacts_db', host='mongodb+srv://erumori:<password>@cluster0.er9eafn.mongodb.net/?retryWrites=true&w=majority')

    num_contacts_to_generate = 5
    contacts = create_fake_contacts(num_contacts_to_generate)
    save_contacts_to_db(contacts)

    for contact in contacts:
        send_contact_to_queue(contact)