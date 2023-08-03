## Проект «foodgram»

## Описание проекта:
Foodgram - это "Продуктовый помощник", который предоставляет возможность пользователям сохранять и публиковать свои рецепты, а также просматривать рецепты, опубликованные другими пользователями. Кроме того, пользователи могут добавлять рецепты в список избранных и формировать список покупок на основе выбранных рецептов.

## Как запустить проект локально в контейнерах
1. Клонировать репозиторий и перейти в него в командной строке
2. Запустить Docker контейнеры:
```
sudo docker-compose up -d --build
```
3. Выполнить миграции
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py load_tags
docker-compose exec backend python manage.py load_ingredients
```
4. Создать суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
5. Прокинуть статику
```
docker-compose exec backend python manage.py collectstatic --no-input
```

## Как запустить проект на вашем сервере:
1. Клонировать репозиторий себе на ПК
2. Подключиться к вашему серверу. Установить на сервере docker.
3. Перенести на сервер файлы docker-compose.yml и nginx.conf
4. Создать и наполнить .env файл на сервере с секретными данными для подключения
5. Запустить контейнеры в демон режиме 
```
sudo docker compose -f docker-compose.yml up -d
```
6. Выполнить миграции, загрузку тегов и ингредиентов в БД, создать суперпользователя.
```
sudo docker-compose exec -t backend python manage.py makemigrations
sudo docker-compose exec -t backend python manage.py migrate
sudo docker-compose exec -t backend python manage.py collectstatic --no-input
sudo docker-compose exec -t backend python manage.py load_tags
sudo docker-compose exec -t backend python manage.py load_ingredients
sudo docker-compose exec backend python manage.py createsuperuser
```