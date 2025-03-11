### 🤖 Описание
Телеграм-бот с использованием Notion API для подготовки к собеседованиям.

Бот парсит конспект и формирует на основе данных специальные карточки.

Реализация метода обучения с помощью карточек, также известный как система Лейтнера. Обычно его используют для запоминания лексики, формул, определений и дат. Однако этот метод не сводится к механическому заучиванию, а помогает организовать учебный процесс. С ним можно быстрее запомнить большое количество информации.

Каждая карточка содержит основную информацию в виде обычного текста и дополнения в виде блока с кодом. Также на карточке указан её номер и группа. Всего групп может быть три:

Группа 1 — карточки с информацией, которую пользователь знает хуже всего. Они будут встречаться чаще всего.
Группа 2 — карточки, которые пользователь немного помнит. Встречаются реже.
Группа 3 — карточки, информацию из которых пользователь помнит лучше всего. Встречаются ещё реже.

### ⚙️ Используемые технологии<a id="technologies-project"></a>:
![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg?style=flat&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-brightgreen.svg)
![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-4.14-brightgreen.svg)
![aiohttp](https://img.shields.io/badge/aiohttp-3.9-brightgreen.svg)

### Работа
![1](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/3e5e6b01-a9f3-4b7c-acde-46e456883324)
![2](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/f0347fc2-40d6-4c79-9d98-ad790961a696)
![3](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/721e81e7-7282-44a9-a784-72ac4d38329a)

### Аутентификация
Для работы с конспектами Notion надо получить интеграционный токен и получить id базы данных согласно документации к Notion API: https://developers.notion.com/docs/getting-started

### 🤸 Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Mikhail0-O/notion_api_bot.git

cd notion_api_bot
```
Cоздать виртуальное окружение:
```
python -m venv venv
```
Активировать виртуальное окружение (Windows):
```
source venv/Scripts/activate
```
Активировать виртуальное окружение (Linux/MacOS):
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip

pip install -r requirements.txt
```
