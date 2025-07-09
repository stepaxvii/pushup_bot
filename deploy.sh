#!/bin/bash

# Скрипт для деплоя бота в Docker Hub

# Конфигурация
DOCKER_USERNAME="your-dockerhub-username"
IMAGE_NAME="bot-pushups"
VERSION="1.0.0"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Начинаем деплой бота в Docker Hub...${NC}"

# Проверяем, что Docker запущен
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker не запущен! Запустите Docker и попробуйте снова.${NC}"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден. Создайте его с переменной TOKEN_BOT${NC}"
    exit 1
fi

# Собираем Docker образ
echo -e "${YELLOW}🔨 Собираем Docker образ...${NC}"
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} .
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Образ успешно собран!${NC}"
else
    echo -e "${RED}❌ Ошибка при сборке образа!${NC}"
    exit 1
fi

# Тестируем образ локально
echo -e "${YELLOW}🧪 Тестируем образ локально...${NC}"
docker run --rm --env-file .env ${DOCKER_USERNAME}/${IMAGE_NAME}:latest python -c "print('✅ Тест успешен!')"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Тест прошел успешно!${NC}"
else
    echo -e "${RED}❌ Тест не прошел!${NC}"
    exit 1
fi

# Пушим в Docker Hub
echo -e "${YELLOW}📤 Пушим образ в Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Образ успешно загружен в Docker Hub!${NC}"
    echo -e "${GREEN}📦 Образ: ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}${NC}"
    echo -e "${GREEN}📦 Образ: ${DOCKER_USERNAME}/${IMAGE_NAME}:latest${NC}"
else
    echo -e "${RED}❌ Ошибка при загрузке в Docker Hub!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Деплой завершен успешно!${NC}"
echo -e "${YELLOW}📋 Для запуска используйте:${NC}"
echo -e "${YELLOW}   docker-compose up -d${NC}" 