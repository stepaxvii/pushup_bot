# 🚀 Деплой Telegram бота

## 📋 Подготовка к деплою

### 1. Настройка Docker Hub

1. Создайте аккаунт на [Docker Hub](https://hub.docker.com/)
2. Войдите в Docker Hub:
   ```bash
   docker login
   ```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:
```bash
TOKEN_BOT=your_telegram_bot_token_here
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Настройка скрипта деплоя

Отредактируйте `deploy.sh`:
```bash
DOCKER_USERNAME="your-dockerhub-username"  # Замените на ваш username
IMAGE_NAME="bot-pushups"
VERSION="1.0.0"
```

## 🔨 Сборка и публикация

### Автоматический деплой

```bash
# Сделайте скрипт исполняемым
chmod +x deploy.sh

# Запустите деплой
./deploy.sh
```

### Ручной деплой

```bash
# 1. Сборка образа
docker build -t your-username/bot-pushups:1.0.0 .
docker build -t your-username/bot-pushups:latest .

# 2. Тестирование
docker run --rm --env-file .env your-username/bot-pushups:latest python -c "print('Test passed')"

# 3. Публикация в Docker Hub
docker push your-username/bot-pushups:1.0.0
docker push your-username/bot-pushups:latest
```

## 🐳 Запуск в продакшене

### Использование docker-compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Использование Docker

```bash
# Запуск Redis
docker run -d --name redis-bot -p 6379:6379 redis:alpine

# Запуск бота
docker run -d \
  --name bot-pushups \
  --env-file .env \
  -v $(pwd)/users.db:/app/users.db \
  -v $(pwd)/bot_pushups.log:/app/bot_pushups.log \
  your-username/bot-pushups:latest

# Запуск планировщика
docker run -d \
  --name bot-scheduler \
  --env-file .env \
  -v $(pwd)/users.db:/app/users.db \
  -v $(pwd)/scheduler.log:/app/scheduler.log \
  your-username/bot-pushups:latest python scheduler.py
```

## 📊 Мониторинг

### Просмотр логов

```bash
# Логи бота
docker logs bot-pushups

# Логи планировщика
docker logs bot-scheduler

# Логи Redis
docker logs redis-bot
```

### Проверка состояния

```bash
# Статус контейнеров
docker ps

# Использование ресурсов
docker stats
```

## 🔧 Обновление

### Обновление образа

```bash
# Остановка сервисов
docker-compose down

# Обновление образа
docker pull your-username/bot-pushups:latest

# Перезапуск
docker-compose up -d
```

### Обновление кода

```bash
# Пересборка и деплой
./deploy.sh

# Перезапуск сервисов
docker-compose down
docker-compose up -d
```

## 🛠️ Troubleshooting

### Проблемы с подключением к Redis

```bash
# Проверка подключения к Redis
docker exec bot-pushups python -c "
import redis
r = redis.Redis(host='redis', port=6379)
print('Redis connection:', r.ping())
"
```

### Проблемы с базой данных

```bash
# Проверка базы данных
docker exec bot-pushups python -c "
import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print('Users count:', cursor.fetchone()[0])
conn.close()
"
```

### Проблемы с токеном бота

```bash
# Проверка переменных окружения
docker exec bot-pushups env | grep TOKEN_BOT
```

## 📝 Структура проекта для деплоя

```
bot-pushups/
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Оркестрация сервисов
├── .dockerignore          # Исключения для Docker
├── deploy.sh              # Скрипт деплоя
├── requirements.txt       # Python зависимости
├── main.py               # Основной файл бота
├── scheduler.py          # Планировщик
├── src/                  # Исходный код
├── .env                  # Переменные окружения
└── README.md            # Документация
```

## 🎯 Готово!

После успешного деплоя ваш бот будет доступен в Docker Hub и готов к развертыванию на любом сервере с Docker. 