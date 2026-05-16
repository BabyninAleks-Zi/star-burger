# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Рабочий сайт: [https://star-burger.online/](https://star-burger.online/)

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Локальная разработка запускается через Docker Compose. Бэкенд и фронтенд работают в разных контейнерах:

- `backend` — Django dev-сервер на Python.
- `frontend` — Node.js и Parcel в режиме `watch`.

Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/) или Docker Engine с Docker Compose plugin.

Скачайте код:

```sh
git clone https://github.com/devmanorg/star-burger.git
cd star-burger
```

Соберите образы:

```sh
docker compose build
```

Примените миграции:

```sh
docker compose run --rm backend python manage.py migrate
```

Если нужна демо-база с товарами, загрузите данные из `dump.json`. Подробности есть в разделе «Перенос данных» ниже.

Запустите сайт:

```sh
docker compose up
```

Откройте сайт в браузере: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Parcel собирает фронтенд из `bundles-src/` в `bundles/`. Django видит собранные файлы через bind mount и отдаёт их как статику. Каталог `media/` тоже подключён через bind mount, поэтому картинки не теряются при перезапуске контейнеров.

Остановить контейнеры:

```sh
docker compose down
```

Полезные команды:

```sh
docker compose ps
docker compose logs backend
docker compose logs frontend
```

## Настройки проекта

Часть настроек проекта берётся из переменных окружения.

Доступные переменные:

- `SECRET_KEY` — секретный ключ Django.
- `DEBUG` — режим отладки (`True`/`False`), по умолчанию `True`.
- `ALLOWED_HOSTS` — список разрешённых хостов через запятую, по умолчанию `127.0.0.1,localhost`.
- `DATABASE_URL` — адрес базы данных в одном URL. Если не задан, используется `db.sqlite3`.
- `YANDEX_GEOCODER_API_KEY` — API-ключ Яндекс Геокодера для расчёта расстояний до ресторанов в интерфейсе менеджера.
- `GEOCODER_CACHE_TTL` — время жизни кэша геокодера в формате `DD HH:MM:SS`, по умолчанию `30 00:00:00`.
- `ROLLBAR_ACCESS_TOKEN` — секретный `post_server_item` токен Rollbar. Если не задан, отправка ошибок в Rollbar отключена.
- `ROLLBAR_ENVIRONMENT` — имя окружения Rollbar. Настраивается отдельно от `DEBUG`, по умолчанию пустое.

Файл `star_burger/.env` добавлен в `.gitignore`, поэтому секреты Rollbar и Django не должны попадать в репозиторий.

## Как запустить production-схему локально

Production-схема описана в `docker-compose.production.yaml`. Она отличается от dev-схемы:

- Django запускается через Gunicorn.
- Postgres запускается в отдельном контейнере.
- Frontend-контейнер делает разовую сборку Parcel и завершается.
- `static` и `media` подключаются как постоянные директории сервера.

Соберите production-образы:

```sh
docker compose -f docker-compose.production.yaml build
```

Соберите frontend:

```sh
docker compose -f docker-compose.production.yaml run --rm frontend
```

Соберите Django static:

```sh
docker compose -f docker-compose.production.yaml run --rm backend python manage.py collectstatic --noinput
```

Примените миграции:

```sh
docker compose -f docker-compose.production.yaml run --rm backend python manage.py migrate --noinput
```

Запустите Postgres и backend:

```sh
docker compose -f docker-compose.production.yaml up -d db backend
```

Проверьте контейнеры:

```sh
docker compose -f docker-compose.production.yaml ps
```

## Деплой на сервер

На сервере Nginx и Certbot работают как обычные программы вне Docker. Docker Compose запускает только приложение: Postgres, Django/Gunicorn и одноразовую сборку фронтенда.

Схема запросов:

- `/static/` отдаётся Nginx из `/var/www/star-burger/static/`.
- `/media/` отдаётся Nginx из `/var/www/star-burger/media/`.
- Остальные запросы Nginx проксирует в Gunicorn на `127.0.0.1:8000`.

Перед первым деплоем установите Docker Engine и Docker Compose plugin на сервер. На локальной машине для продвинутого деплоя тоже нужен Docker CLI с Compose plugin: локальный клиент будет отправлять команды удалённому Docker Engine по SSH.

Создайте директории для файлов, которые должны жить дольше контейнеров:

```sh
mkdir -p /var/www/star-burger/static
mkdir -p /var/www/star-burger/media
```

Настройте Nginx для сайта:

```nginx
location /static/ {
    alias /var/www/star-burger/static/;
}

location /media/ {
    alias /var/www/star-burger/media/;
}

location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Проверьте и перезагрузите Nginx:

```sh
nginx -t
systemctl reload nginx
```

### Продвинутый деплой с локальной машины

Скрипт `deploy_remote_docker.sh` запускается локально, но собирает образы и запускает контейнеры на сервере через `DOCKER_HOST=ssh://root@77.105.170.71`. Он не делает `git pull` на сервере: локальный Docker-клиент отправляет текущий build context удалённому Docker Engine.

Перед запуском закоммитьте изменения: скрипт останавливается, если в рабочем дереве есть незакоммиченные файлы. Это нужно, чтобы хэш в Rollbar соответствовал реально задеплоенному коду.

Запустите деплой:

```sh
bash deploy_remote_docker.sh
```

Если сервер отличается от стандартного, передайте его через переменную окружения:

```sh
SERVER=root@example.com bash deploy_remote_docker.sh
```

Скрипт:

1. Проверяет чистоту git-дерева.
2. Подключается к удалённому Docker Engine через SSH.
3. Создаёт директории `/var/www/star-burger/static` и `/var/www/star-burger/media` на сервере.
4. Собирает Docker-образы на сервере из локального build context.
5. Собирает frontend через отдельный Node/Parcel-контейнер.
6. Запускает `collectstatic`.
7. Применяет миграции.
8. Запускает `db` и `backend` через Docker Compose.
9. Отправляет уведомление о деплое в Rollbar.

Compose запускается с project name `app`, чтобы использовать те же контейнеры и volumes, что и серверный деплой.

### Деплой через SSH на сервер

Это запасной способ: подключиться на сервер и запустить деплойный скрипт там.

Подключитесь к серверу:

```sh
ssh root@77.105.170.71
```

Перейдите в каталог проекта и запустите деплой:

```sh
cd /srv/star-burger/app
bash deploy_star_burger.sh
```

Скрипт `deploy_star_burger.sh`:

1. Обновляет код через `git pull --ff-only`.
2. Создаёт директории `/var/www/star-burger/static` и `/var/www/star-burger/media`.
3. Собирает Docker-образы на сервере.
4. Собирает frontend через отдельный Node/Parcel-контейнер.
5. Запускает `collectstatic`.
6. Применяет миграции.
7. Запускает `db` и `backend` через Docker Compose.
8. Отправляет уведомление о деплое в Rollbar.

Проверить состояние контейнеров на сервере:

```sh
docker compose -f docker-compose.production.yaml ps
```

## Перенос данных

Миграции создают таблицы, но не переносят записи. Для наполнения новой Docker-базы загрузите `dump.json`.

Если `dump.json` сохранён в UTF-16, сначала перекодируйте его в UTF-8:

```sh
iconv -f UTF-16 -t UTF-8 dump.json -o dump_utf8.json
docker compose -f docker-compose.production.yaml cp dump_utf8.json backend:/tmp/dump_utf8.json
docker compose -f docker-compose.production.yaml exec backend python manage.py loaddata /tmp/dump_utf8.json
```

Если русские строки загрузились с битым текстом, исправьте кодировку содержимого:

```sh
python3 - <<'PY'
from pathlib import Path

source = Path('dump.json')
target = Path('dump_fixed.json')

text = source.read_text(encoding='utf-16')
fixed_text = text.encode('cp866').decode('cp1251')

target.write_text(fixed_text, encoding='utf-8')
print(f'Written {target}')
PY
```

Затем загрузите исправленный файл:

```sh
docker compose -f docker-compose.production.yaml cp dump_fixed.json backend:/tmp/dump_fixed.json
docker compose -f docker-compose.production.yaml exec backend python manage.py loaddata /tmp/dump_fixed.json
```

Картинки из старой папки `media/` перенесите в production-директорию:

```sh
cp -a /srv/star-burger/app/media/. /var/www/star-burger/media/
```

## Проверить Rollbar

Для отправки уведомления о деплое задайте в `star_burger/.env`:

```env
ROLLBAR_ACCESS_TOKEN=your-rollbar-post-server-item-token
ROLLBAR_ENVIRONMENT=production
```

После успешного запуска `bash deploy_remote_docker.sh` или `bash deploy_star_burger.sh` в Rollbar должен появиться deploy с хэшем последнего коммита.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
