# Инструкция для запуска проекта на чистом Ubuntu

!!! Docker образы могут не загружаться в России, поэтому используйте средства обхода или сервер в другой стране.

### Зависимости

1. Для запуска проекта нужен docker и docker-compose
2. Упрощенное управление проектом реализовано через Makefile, поэтому нужна утилита для использования этих команд. На Ubuntu необходимо установить модуль make

```bash
sudo apt install make
```

### Переменные окружения

В проекте уже есть заполненные тестовые файлы. Для применения выполните команды (bash) в корне проекта. Больше ничего менять не нужно

```bash
cp env.db .env.db
cp app/.env app/.env
```

Структура файлов

1. .env.db

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres
PGPORT=5432

REDIS_URL=redis://redis:6379/
```

2. app/.env

```
DEBUG=1

ALLOWED_HOSTS=localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_CONN_MAX_AGE=360

SECRET_KEY=
```

### Запуск и сборка проекта

Выполните код в терминале, находясь в корне проекта:

```bash
make up-build
```

Если вы хотите сразу видеть логи, для запуска используйте данную команду:

```bash
make run-build
```

В дальнейшем можно сразу запускать проект, не тратя время и ресурсы на сборку:

```bash
make up
make run
```

### После первого запуска

Сразу после запуска необходимо выполнить миграции БД:

```bash
make m
```

### Выключение проекта

```bash
make down
```

### Дополнительные команды

Перезапуск и перезапуск со сборкой:

```bash
make restart
make restart-build
```

Просматривать логи:

```bash
make logs
```
