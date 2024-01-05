# Django-Aiogram-Telegram-Bot version  0.1.0

### Установка и запуск
1. Клонируйте репозиторий с проектом на локальную машину или удалённый сервер
2. Добавьте в корень проекта файл с секретной информацией <font color=green>.env.local</font> заполнив его по [примеру](.env.default)
3. Запустите Docker контейнеры с базой данных и Redis
4. Создайте и активируйте виртуальное окружение
5. Запустите авто тесты для проверки работоспособности
6. Запустите приложение

#### Запуск Docker контейнеров
```shell
docker/up.sh
```
#### Создание виртуального окружения и его активация
```shell
poetry config virtualenvs.in-project true
```
```shell
poetry install
```
```shell
poetry shell
```
#### Запуск авто тестов
```shell
pytest src/tests
```
#### Запуск приложения
* Для разработки:\
<font size = 2>запускает Uvicorn</font>,
<font size = 2>при необходимости измените хост(FASTAPI_HOST) и порт(FASTAPI_PORT) в [settings.py](config/settings.py "файл основных настроек проекта")</font>
```shell
python main.py
```
<font size = 2>для проверки перейдите по ссылке [http://0.0.0.0:8000/ping](http://0.0.0.0:8000/ping "метод проверки подключения")</font>
