### Описание
Телеграм-бот для парсинга конспекта.

### Работа


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