# Aviation Dashboard

Система мониторинга авиарейсов с визуализацией в Metabase

## Описание проекта

Проект предназначен для сбора данных о пролетающих рейсах над заданным регионом (по умолчанию - Чёрное море) с последующей визуализацией в Metabase. Система состоит из следующих компонентов:

1. **Монитор рейсов** - Python-скрипт, собирающий данные с Flightradar24 API
2. **База данных** - PostgreSQL для хранения информации о рейсах, аэропортах и авиакомпаниях
3. **Визуализация** - Metabase для анализа и отображения данных

##Визуализация в metabase
![2025-04-03_19-47-22](https://github.com/user-attachments/assets/8cfcd678-2bcb-4713-b8b9-b13e0b6e2293)
![2025-04-03_19-47-01](https://github.com/user-attachments/assets/c375852e-b9d6-4174-847b-88c8b56661d8)
![2025-04-03_15-13-48](https://github.com/user-attachments/assets/9e1d27e7-5a07-4282-8449-3cba89fca576)


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
!!!В папке damp присутсвует выгрузка из бд flightbd и metabase_db!!!

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
