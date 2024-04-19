FROM rabbitmq:3-management

# Устанавливаем переменные окружения для учетных данных RabbitMQ
ENV RABBITMQ_USER=user
ENV RABBITMQ_PASSWORD=user
ENV RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbitmq.pid

# Копирование конфигурационных файлов и скрипта инициализации
COPY rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY certs/ /etc/rabbitmq/certs/
COPY init.sh /init.sh

# Устанавливаем права на выполнение скрипта инициализации
RUN chmod +x /init.sh

# Определяем точку входа и команду
CMD ["/init.sh"]

# Объявление используемых портов
EXPOSE 5671 15672
