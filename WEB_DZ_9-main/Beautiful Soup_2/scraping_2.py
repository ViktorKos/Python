import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


# Функція для отримання цитат зі сторінки
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


# Функція для отримання цитат з усіх сторінок сайту
def scrape_quotes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("Щось пішло не так", err)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_data = get_quotes(soup)

    # Перевірка наявності посилання на наступну сторінку
    next_page_link = soup.find('li', class_='next')
    while next_page_link:
        next_page_url = urljoin(url, next_page_link.find('a')['href'])

        try:
            response = requests.get(next_page_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("Щось пішло не так", err)
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        quotes_data += get_quotes(soup)
        next_page_link = soup.find('li', class_='next')

    return quotes_data


# Функція для отримання даних про авторів з усіх сторінок сайту
def scrape_authors(url, visited_authors=None):
    if visited_authors is None:
        visited_authors = set()

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("Щось пішло не так", err)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    authors = soup.find_all('div', class_='quote')

    authors_data = []
    for author in authors:
        author_url = urljoin(url, author.find('a')['href'])

        if author_url in visited_authors:
            continue

        visited_authors.add(author_url)

        try:
            author_response = requests.get(author_url)
            author_response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("Щось пішло не так", err)
            continue

        author_soup = BeautifulSoup(author_response.text, 'html.parser')
        fullname_element = author_soup.find('h3', class_='author-title')
        if not fullname_element:
            print("Ім'я автора не знайдено")
            continue

        fullname = fullname_element.get_text(strip=True)
        born_date_element = author_soup.find('span', class_='author-born-date')
        born_date = born_date_element.get_text(strip=True) if born_date_element else ""
        born_location_element = author_soup.find('span', class_='author-born-location')
        born_location = born_location_element.get_text(strip=True) if born_location_element else ""
        description_element = author_soup.find('div', class_='author-description')
        description = description_element.get_text(strip=True) if description_element else ""

        authors_data.append({
            'fullname': fullname,
            'born_date': born_date,
            'born_location': born_location,
            'description': description
        })

    next_page = soup.find('li', class_='next')
    if next_page:
        next_page_url = urljoin(url, next_page.find('a')['href'])
        authors_data += scrape_authors(next_page_url, visited_authors)

    # Сортуємо авторів за ім'ям
    authors_data.sort(key=lambda x: x['fullname'].lower())
    return authors_data


# Головна функція
def main():
    url = 'http://quotes.toscrape.com'
    quotes_data = scrape_quotes(url)
    authors_data = scrape_authors(url)

    try:
        with open('quotes.json', 'w', encoding="UTF-8") as f:
            json.dump(quotes_data, f, ensure_ascii=False, indent=2)
    except IOError:
        print("Помилка запису до файлу quotes.json")

    try:
        with open('authors.json', 'w', encoding="UTF-8") as f:
            json.dump(authors_data, f, ensure_ascii=False, indent=2)
    except IOError:
        print("Помилка запису до файлу authors.json")


if __name__ == "__main__":
    main()
