### Описание
Телеграм-бот для парсинга конспекта.

### Работа
![1](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/3e5e6b01-a9f3-4b7c-acde-46e456883324)
![2](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/f0347fc2-40d6-4c79-9d98-ad790961a696)
![3](https://github.com/Mikhail0-O/notion_api_bot/assets/156952363/721e81e7-7282-44a9-a784-72ac4d38329a)

### Аутентификация
Для работы с конспектами Notion надо получить интеграционный токен и получить id базы данных

### Документация к Notion API: https://developers.notion.com/docs/getting-started


### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Mikhail0-O/notion_api_bot.git

cd yatube_api
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv

source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip

pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
