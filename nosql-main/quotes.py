from mongoengine import connect
from main import Quote

def search_quotes(query):
    if query.startswith("name:"):
        author_name = query.split(":")[1].strip()
        quotes = Quote.objects(author__fullname=author_name)
    elif query.startswith("tag:"):
        tag = query.split(":")[1].strip()
        quotes = Quote.objects(tags=tag)
    elif query.startswith("tags:"):
        tags = query.split(":")[1].strip().split(',')
        quotes = Quote.objects(tags__in=tags)
    else:
        print("Invalid query format. Please use 'name:', 'tag:', or 'tags:'.")
        return

    for quote in quotes:
        print(f"{quote.author.fullname}: {quote.quote}")

if __name__ == "__main__":
    connect('quotes_db', host='mongodb+srv://erumori:<password>@cluster0.er9eafn.mongodb.net/?retryWrites=true&w=majority')

    while True:
        user_input = input("Enter command (type 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            break
        else:
            search_quotes(user_input)