Для поднятия сервиса нужно запустить команду:

docker compose -f docker-compose.yaml up -d

Для удаления контейнера:

docker compose -f docker-compose.yaml down --remove-orphans

Для накатывания миграций:
alembic revision --autogenerate -m

alembic revision upgrade head

Эта команда пересоберет и перезапустит user-registration-service без перезапуска зависимых сервисов (register_service_db, rabbitmq).
docker-compose up -d --no-deps --build authentication-service

Если нужно пересобрать сервис и все от которых он зависит:
docker-compose up -d --build <service_name>

Для остановки и удаления конкретного сервиса (с удалением контейнеров):
docker-compose stop <service_name>
docker-compose rm <service_name>

Чтобы поднять и запустить только контейнеры баз данных аутентификации (auth_service_db), регистрации (register_service_db), а также RabbitMQ и Redis 
docker-compose up -d register_service_db auth_service_db rabbitmq auth_redis

Если вы внесете изменения в конфигурацию одного из сервисов и хотите пересоздать только его, можно добавить флаг --build для пересборки образа перед запуском:
docker-compose up -d --build register_service_db

Просмотр состояния контейнеров:
docker-compose ps

Показывает логи для всех контейнеров. Если вы хотите увидеть логи конкретного сервиса:
docker-compose logs <service_name>

Для непрерывного отслеживания логов (в реальном времени) добавьте флаг -f:
docker-compose logs -f <service_name>

Статистика использования ресурсов:
docker-compose stats

Здесь можно получить детализированную информацию о контейнере, включая состояние сети, настройки монтажа (volumes), переменные окружения и многое другое.
docker inspect <container_id_or_name>

Показывает события, происходящие в системе Docker в реальном времени, такие как создание, запуск, остановка контейнеров и другие изменения.
docker events


1. Использование Redis CLI
Шаг 1: Подключение к контейнеру Docker
Сначала вам нужно подключиться к контейнеру Docker, в котором работает Redis. Вы можете сделать это с помощью следующей команды:
docker exec -it <container_name_or_id> /bin/bash
docker exec -it auth_redis /bin/sh
2. Шаг 2: Запуск Redis CLI
После того как вы подключились к контейнеру, запустите Redis CLI командой:
redis-cli


