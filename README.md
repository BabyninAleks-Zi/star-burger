# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Как собрать бэкенд

Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

Перейдите в каталог проекта:
```sh
cd star-burger
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.10.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`


Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```

Часть настроек проекта берётся из переменных окружения.
Создайте файл `.env` в каталоге `star_burger/` и добавьте туда переменные в формате `KEY=value`.

Доступные переменные:

- `SECRET_KEY` — секретный ключ Django.
- `DEBUG` — режим отладки (`True`/`False`), по умолчанию `True`.
- `ALLOWED_HOSTS` — список разрешённых хостов через запятую, по умолчанию `127.0.0.1,localhost`.
- `DATABASE_URL` — адрес базы данных в одном URL, например `postgres://USER:PASSWORD@HOST:PORT/DBNAME`. Если не задан, используется `db.sqlite3`.
- `YANDEX_GEOCODER_API_KEY` — API-ключ Яндекс Геокодера для расчёта расстояний до ресторанов в интерфейсе менеджера.
- `GEOCODER_CACHE_TTL` — время жизни кэша геокодера в формате `DD HH:MM:SS`, по умолчанию `30 00:00:00`.
- `ROLLBAR_ACCESS_TOKEN` — секретный `post_server_item` токен Rollbar. Если не задан, отправка ошибок в Rollbar отключена.
- `ROLLBAR_ENVIRONMENT` — имя окружения Rollbar, по умолчанию `development` при `DEBUG=True` и `production` при `DEBUG=False`.

Пример:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://star_burger_user:change-me@localhost:5432/star_burger
YANDEX_GEOCODER_API_KEY=your-yandex-key
GEOCODER_CACHE_TTL=30 00:00:00
ROLLBAR_ACCESS_TOKEN=your-rollbar-post-server-item-token
ROLLBAR_ENVIRONMENT=development
```

Создайте файл базы данных SQLite и отмигрируйте её следующей командой:

```sh
python manage.py migrate
```

Запустите сервер:

```sh
python manage.py runserver
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.

### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточны, и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.


## Как запустить prod-версию сайта

Собрать фронтенд:

```sh
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

Настроить бэкенд: создать файл `.env` в каталоге `star_burger/` со следующими настройками:

- `DEBUG` — дебаг-режим. Поставьте `False`.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts)
- `DATABASE_URL` — адрес Postgres в формате `postgres://USER:PASSWORD@HOST:PORT/DBNAME`.
- `ROLLBAR_ACCESS_TOKEN` — `post_server_item` токен Rollbar для отправки ошибок.
- `ROLLBAR_ENVIRONMENT` — имя окружения Rollbar. Для боевого сервера используйте `production`.

Пример prod-настроек:

```env
SECRET_KEY=long-random-production-secret
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgres://star_burger_user:strong-production-password@localhost:5432/star_burger
ROLLBAR_ACCESS_TOKEN=your-rollbar-post-server-item-token
ROLLBAR_ENVIRONMENT=production
```

Файл `star_burger/.env` добавлен в `.gitignore`, поэтому секреты Rollbar и Django не должны попадать в репозиторий.

### Проверить Rollbar

Для проверки локальной dev-версии задайте в `star_burger/.env`:

```env
DEBUG=True
ROLLBAR_ACCESS_TOKEN=your-rollbar-post-server-item-token
ROLLBAR_ENVIRONMENT=development
```

Запустите сайт и спровоцируйте ошибку 500. В Rollbar должно появиться событие с окружением `development`.

Для проверки prod-версии на сервере задайте:

```env
DEBUG=False
ROLLBAR_ACCESS_TOKEN=your-rollbar-post-server-item-token
ROLLBAR_ENVIRONMENT=production
```

Перезапустите приложение:

```sh
systemctl restart star-burger
```

После ошибки 500 в Rollbar должно появиться событие с окружением `production`.

### Перенести данные из SQLite в Postgres

Перед переключением базы выгрузите данные из текущей SQLite-базы:

```sh
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  -e contenttypes \
  -e auth.Permission \
  --indent 2 \
  > dump.json
```

Создайте базу и пользователя Postgres. Пример для Linux:

```sh
sudo -u postgres psql
```

```sql
CREATE USER star_burger_user WITH PASSWORD 'strong-password';
CREATE DATABASE star_burger OWNER star_burger_user;
\q
```

Добавьте в `star_burger/.env`:

```env
DATABASE_URL=postgres://star_burger_user:strong-password@localhost:5432/star_burger
```

Примените миграции уже в Postgres и загрузите данные:

```sh
python manage.py migrate
python manage.py loaddata dump.json
```

После успешной проверки сайт должен работать без файла `db.sqlite3`. Пароль в `DATABASE_URL` на сервере должен отличаться от примеров из README.

### Быстрое обновление кода на сервере

Подключитесь к серверу:

```sh
ssh root@77.105.170.71
```

Перейдите в каталог проекта и запустите деплой:

```sh
cd /srv/star-burger/app
./deploy_star_burger.sh
```

Скрипт обновит код, установит зависимости, пересоберёт фронтенд и статику Django, применит миграции и перезапустит сервис star-burger

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
