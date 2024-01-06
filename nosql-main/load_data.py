import json
from mongoengine import connect
from main import Author, Quote

def load_authors(filename):
    with open(filename, 'r') as file:
        authors_data = json.load(file)
        for author_data in authors_data:
            author = Author(**author_data)
            author.save()

def load_quotes(filename):
    with open(filename, 'r') as file:
        quotes_data = json.load(file)
        for quote_data in quotes_data:
            author_fullname = quote_data['author']
            author = Author.objects(fullname=author_fullname).first()
            if author:
                quote_data['author'] = author
                quote = Quote(**quote_data)
                quote.save()

if __name__ == "__main__":
    connect('mongodb+srv://erumori:<password>@cluster0.er9eafn.mongodb.net/?retryWrites=true&w=majority')
    load_authors('authors.json')
    load_quotes('quotes.json')