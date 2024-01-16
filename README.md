# Leader-Team-AI-bot version  0.1.0

### Установка и запуск
1. Клонируйте репозиторий с проектом на локальную машину или удалённый сервер
2. Добавьте в директорию env файл с секретной информацией <font color=green>.env.local</font> заполнив его по [примеру](env/.env.default)
3. Запустите Docker контейнеры с базой данных и Redis
4. Создайте и активируйте виртуальное окружение
5. Запустите приложение

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
#### Запуск Телеграм бота
```shell
python manage.py start_tg_bot
```