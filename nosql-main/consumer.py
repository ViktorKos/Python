import json
from mongoengine import connect, Document, StringField, BooleanField
import pika


class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(default=False)


def callback(ch, method, properties, body):
    message = json.loads(body.decode('utf-8'))
    contact_id = message.get('contact_id')

    if contact_id:
        contact = Contact.objects(id=contact_id, message_sent=False).first()
        if contact:
            # Simulate sending email (replace with actual email sending logic)
            print(f"Simulating email sending to {contact.email}")

            # Update the contact status after sending the email
            contact.update(set__message_sent=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connect('contacts_db', host='mongodb+srv://erumori:<password>@cluster0.er9eafn.mongodb.net/?retryWrites=true&w=majority')

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='contacts_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='contacts_queue', on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()