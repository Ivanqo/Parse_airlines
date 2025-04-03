# Aviation Dashboard

Система мониторинга авиарейсов с визуализацией в Metabase

## Описание проекта

Проект предназначен для сбора данных о пролетающих рейсах над заданным регионом (по умолчанию - Чёрное море) с последующей визуализацией в Metabase. Система состоит из следующих компонентов:

1. **Монитор рейсов** - Python-скрипт, собирающий данные с Flightradar24 API
2. **База данных** - PostgreSQL для хранения информации о рейсах, аэропортах и авиакомпаниях
3. **Визуализация** - Metabase для анализа и отображения данных

## Функциональность

- Регулярный сбор данных о пролетающих рейсах
- Сохранение информации о:
  - Номере рейса (call sign)
  - Аэропортах вылета и назначения
  - Модели самолёта
  - Авиакомпании
  - Времени вылета/прилёта
  - Статусе рейса
- Автоматическое обновление данных в реальном времени
- Визуализация маршрутов и статистики в Metabase

## Технологии

- Python 3
- PostgreSQL
- Metabase
- Docker
- Flightradar24 API

## Запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Ivanqo/aviation-dashboard.git
cd aviation-dashboard
```
2. Запустите сервисы:
```
bash
Copy
docker-compose up -d
После запуска будут доступны:

Metabase: http://localhost:3000
Metabase Local данные для входа:
    ivan.basenko.05@mail.ru
    MQZ-b7w-uHv-M7c
PostgreSQL: postgres:5432 (логин/пароль: postgres/postgres)
```
