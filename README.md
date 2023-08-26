# Проект «Книга рецептов» - RecipeBook

### Описание проекта
Проект представляет собой онлайн-сервис и API для него. Сервис позволяет публиковать любимые рецепты, подписываться на других авторов, составлять список из избранных рецептов, а перед походом в магазин - скачивать сводный список продуктов для выбранных рецептов.
Проект запущен на виртуальном удалённом сервере в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Заготовленный контейнер с фронтендом используется для сборки файлов. Контейнер с проектом обновляется на Docker Hub.

### Технологический стек
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=cd5c5c)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=0095b6)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=cd5c5c)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=0095b6)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=cd5c5c)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=0095b6)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=cd5c5c)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=0095b6)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=cd5c5c)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=0095b6)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=cd5c5c)](https://cloud.yandex.ru/)

### Запуск проекта в контейнерах
- Клонирование удаленного репозитория
```bash
git@github.com:AnnaMihailovna/foodgram-project-react.git
cd infra
```
- В директории /infra создайте файл .env с переменными окружения
- Сборка и развертывание контейнеров
```bash
docker compose up -d --build
```
- Выполните миграции, соберите статику, создайте суперпользователя
```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /app/backend_static/static/
docker compose exec backend python manage.py createsuperuser
```
- Наполните базу данных ингредиентами и тегами
```bash
docker compose exec backend python manage.py import
```

### Суперпользователь:
Логин: ```admin``` 

Email: ```admin@admin.xx```  
Пароль: ```1234``` 

### Тестовые пользователи:
Логин: ```user3new```  
Email: ```user3@user.xx```  
Пароль: ```user3123456```

--------------------------
Логин: ```user7new```  
Email: ```user7@user.xx```  
Пароль: ```user7123456```

--------------------------
Логин: ```user9new```  
Email: ```user9@user.xx```  
Пароль: ```user9123456```

## Ссылки
### Документация API проекта:
http://recipebook.hopto.org/api/docs/redoc.html

### Развёрнутый проект:
http://recipebook.hopto.org

http://recipebook.hopto.org/admin/

### Автор бэкенда и деплой
[AnnaMihailovna](https://github.com/AnnaMihailovna/)
