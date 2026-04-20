# Сайт доставки Star Burger

Сайт сети ресторанов Star Burger. Пользователь может оформить заказ, а менеджер обработать его в интерфейсе управления.

## Запуск

Для запуска сайта понадобится Python 3.10+.

Установите зависимости:

```sh
pip install -r requirements.txt
```

Примените миграции:

```sh
python manage.py migrate
```

Запустите сервер:

```sh
python manage.py runserver
```

Сайт будет доступен по адресу:

- Главная страница: `http://127.0.0.1:8000/`
- Админка: `http://127.0.0.1:8000/admin/`
- Интерфейс менеджера: `http://127.0.0.1:8000/manager/orders/`
- Browsable API: `http://127.0.0.1:8000/api/order/`

## Переменные окружения

Часть настроек проекта берётся из переменных окружения.
Создайте файл `.env` в каталоге `star_burger/` и добавьте туда переменные в формате `KEY=value`.

Доступные переменные:

- `SECRET_KEY` — секретный ключ Django.
- `DEBUG` — режим отладки (`True`/`False`), по умолчанию `True`.
- `ALLOWED_HOSTS` — список разрешённых хостов через запятую, по умолчанию `127.0.0.1,localhost`.
- `YANDEX_GEOCODER_API_KEY` — API-ключ Яндекс Геокодера для расчёта расстояний до ресторанов в интерфейсе менеджера.
- `GEOCODER_CACHE_TTL` — время жизни кэша геокодера в формате `DD HH:MM:SS`, по умолчанию `30 00:00:00`.

Пример:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
YANDEX_GEOCODER_API_KEY=your-yandex-key
GEOCODER_CACHE_TTL=30 00:00:00
```
