import json
import requests
from bs4 import BeautifulSoup


# Базовий URL сайту з цитатами
BASE_URL = "http://quotes.toscrape.com"

# Списки для зберігання цитат та авторів
QUOTES = []
AUTHORS = []

# Назви файлів для зберігання даних
DATA_QUOTES = "quotes.json"
DATA_AUTHORS = "authors.json"


# Функція для отримання HTML-контенту сторінки
def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = BeautifulSoup(response.content, 'html.parser')
        return content


# Функція для отримання цитат з HTML-контенту
def get_quotes(content):
    quote_data = []
    quotes = content.find_all('div', class_='quote')
    for q in quotes:
        author = q.find('small', class_='author').get_text(strip=True)
        quote = q.find('span', class_='text').get_text(strip=True)
        tags_elements = q.find('div', class_='tags').find_all('a', class_='tag')
        tags = [tag.get_text(strip=True) for tag in tags_elements]
        quote_data.append({"tags": tags, "author": author, "quote": quote})
    return quote_data


# Функція для отримання авторів з HTML-контенту
def get_authors(content):
    authors_data = []
    authors = content.find_all('div', class_='quote')
    for author in authors:
        author_link = author.find('a')['href']
        author_url = BASE_URL + author_link
        # Отримуємо HTML-контент сторінки автора
        author_response = get_page_content(author_url)
        fullname = author_response.find('h3', class_='author-title').get_text(strip=True)
        born_date = author_response.find('span', class_='author-born-date').get_text()
        born_location = author_response.find('span', class_='author-born-location').get_text(strip=True)
        description = author_response.find("div", class_='author-description').get_text(strip=True)
        authors_data.append({"fullname": fullname, "born_date": born_date,
                             "born_location": born_location, "description": description})
    return authors_data


# Функція для збереження даних у JSON-файл
def save_to_json(data, filename):
    with open(filename, "w", encoding="UTF-8") as fd:
        json.dump(data, fd, ensure_ascii=False, indent=4)


# Функція для отримання унікальних авторів
def unique_authors_data(authors):
    # Перетворення кожного словника на кортеж й створення множини
    unique_author_tuples = {tuple(author.items()) for author in authors}
    # Перетворення назад до списку словників
    unique_authors = [dict(author_tuple) for author_tuple in unique_author_tuples]
    return unique_authors


# Головна функція, яка керує процесом
def main():
    # Обробка першої сторінки
    page_content = get_page_content(BASE_URL)

    while True:
        # Отримання цитат та авторів з поточної сторінки
        QUOTES.extend(get_quotes(page_content))
        AUTHORS.extend(get_authors(page_content))

        # Перевірка наявності посилання на наступну сторінку
        next_page_link = page_content.find('li', class_='next')
        if next_page_link is None:
            break

        # Якщо посилання існує, додаємо його сигнатуру до базового лінку
        next_page_url = BASE_URL + next_page_link.find('a')['href']
        page_content = get_page_content(next_page_url)

    # Збереження отриманих даних у файли
    save_to_json(QUOTES, DATA_QUOTES)
    save_to_json(unique_authors_data(AUTHORS), DATA_AUTHORS)


# Виклик головної функції
if __name__ == "__main__":
    main()
