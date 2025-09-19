# QuoteShooter 

Веб-приложение на Django для случайного отображения цитат с системой лайков, дизлайков и топ-рейтингов.

## Стек
- **Backend**: Django 5, Python 3.11
- **Database**: PostgreSQL 15 (в Docker)
- **Frontend**: HTML + CSS + JS (Vanilla, AJAX)
- **Инфраструктура**: Docker, Docker Compose
- **Логирование**: кастомный `logger`

---

## Функционал

### Главная страница:

- Случайная цитата (выбор с учётом веса).
- Счётчик просмотров увеличивается при показе.
- Кнопка "Дальше" — загрузка новой случайной цитаты без перезагрузки страницы.

### Голосование:

- Лайки ❤️ и дизлайки 👎 для каждой цитаты.
- AJAX-обновление без перезагрузки.
- Анимация при изменении счётчиков.

### Топ-рейтинги:

- Топ-N цитат по просмотрам 🔥.
- Топ-N цитат по лайкам ❤️.
- Быстрые ссылки на "Топ-10".

### Добавление цитаты:

- Форма с полями: автор, название произведения, текст.
- Автоматическое создание источника (Source).

### Админка Django:

- Управление цитатами и источниками.

### Обработка ошибок:

- Кастомная страница 404.
- Логирование действий (создание цитат, ошибки, выбор случайных записей).

---

## Локальные установка и запуск

### 1. Клонируем репозиторий
```bash
git clone https://github.com/jw-mans/IT-Solution_PythonDev-test.git
cd quoteshooter
```
### 2. Создаём файл окружения
В папке `quoteshooter/` должен быть файл `.env`:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=quotes
POSTGRES_USER=quotes_user
POSTGRES_PASSWORD=quotes_password
DB_HOST=db
DB_PORT=5432
```
### 3. Поднимаем контейнеры
```bash
docker compose up -d --build
```
### 4. Применяем миграции
```bash
docker-compose exec web python quoteshooter/manage.py makemigrations quoter
docker-compose exec web python quoteshooter/manage.py migrate
```
### 5. Запускаем сервер
```bash
docker-compose exec web python quoteshooter/manage.py runserver 0.0.0.0:8000
```
На главную страницу переходим по адресу `http://localhost:8000`
### 6. Для создания админки:
```bash
docker-compose exec web python quoteshooter/manage.py createsuperuser
```
