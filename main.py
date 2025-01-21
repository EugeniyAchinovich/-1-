import requests

NEWS_API_KEY = "1040152cab044b81a98a56c7da7acb54"  # Ваш ключ
url = 'https://newsapi.org/v2/top-headlines'
params = {
    'apiKey': NEWS_API_KEY,
    'country': 'us',  # Замените на 'ru' для России или другую страну
}

response = requests.get(url, params=params)
print(response.url)  # Печатает URL запроса
print(response.status_code)  # Печатает статус ответа

if response.status_code == 200:
    articles = response.json().get('articles', [])
    print(articles)  # Печатает полученные статьи
else:
    print("Ошибка:", response.json())