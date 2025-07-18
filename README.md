# 🚢 Export NorthWest Scripts

## 📋 Описание репозитория

Репозиторий `export_nw_scripts` содержит набор скриптов для автоматизированной обработки экспортных данных NorthWest. Система предназначена для:

- 📊 Преобразования Excel файлов с данными о грузоперевозках в формат JSON
- 🌐 Обогащения данных информацией о портах через внешние API
- 🏷️ Унификации названий судоходных линий
- 🤖 Автоматической обработки файлов в режиме демона

## 📁 Структура проекта

```
export_nw_scripts/
├── bash_dir/                    # Bash скрипты для автоматизации
│   ├── flat_export_nw.sh       # Основной скрипт обработки файлов
│   └── run_export_nw.sh        # Демон для непрерывной работы
├── scripts/                     # Python модули
│   ├── flat_export_nw.py       # Основной модуль конвертации Excel → JSON
│   └── parsed.py               # Модуль парсинга и обогащения данных
├── Dockerfile                   # Конфигурация Docker контейнера
├── requirements.txt             # Python зависимости
└── README.md                   # Данный файл
```

## ⚙️ Блоки работ

### 1. 📄➡️📋 Конвертация данных (flat_export_nw.py)

**Назначение:** Преобразование Excel файлов с экспортными данными в структурированный JSON формат.

**Функциональность:**
- 📖 Чтение Excel файлов (.xls, .xlsx)
- 🔄 Переименование колонок с русских названий на английские
- 🧹 Очистка и валидация данных
- 📝 Добавление метаданных (имя файла, время обработки)
- 🔀 Конвертация направлений: "импорт" → "import", "экспорт" → "export", "каботаж" → "cabotage"
- 💾 Сохранение в JSON формате

**Обрабатываемые поля:**
- 📅 Год, Месяц, Линия, Судно, Рейс
- 🏭 Порт, Отправитель, Получатель, Экспедитор
- 📦 Груз, Тип/Размер контейнера, Количество контейнеров
- 🏢 Терминал, TEU, Номер контейнера
- 📄 ГТД, ТНВЭД коды и группы
- 🆔 ИНН, Страна компании, Направление
- 📃 Коносамент, Вес нетто

### 2. 🔍⭐ Обогащение данных (parsed.py)

**Назначение:** Дополнительная обработка и обогащение данных через внешние сервисы.

**Функциональность:**
- 🔗 Унификация названий судоходных линий через ClickHouse
- 🌐 Получение информации о портах через HTTP API
- 🔍 Определение типа коносамента по судоходной линии
- 🚫 Фильтрация пустых контейнеров
- 🔄 Повторные попытки запросов при ошибках

**Поддерживаемые линии:**
- 🚢 SINOKOR / HEUNG-A LINE
- 🚢 MSC
- 🚢 ARKAS
- 🚢 REEL SHIPPING
- 🚢 SAFETRANS

### 3. 🤖⚡ Автоматизация обработки (bash скрипты)

**flat_export_nw.sh:**
- 👀 Мониторинг директорий с входящими файлами
- 📂 Создание структуры папок (done/, json/)
- ⏱️ Обработка файлов с отступом безопасности (3 секунды)
- ✅ Перемещение обработанных файлов в папку done/
- ❌ Обработка ошибок (файлы с ошибками → error_*)

**run_export_nw.sh:**
- 🔄 Демон для непрерывной работы
- ⚡ Циклический запуск обработки каждую секунду

## 🛠️ Требования к окружению

### 🔧 Переменные окружения

```bash
# Пути к данным
export XL_IDP_PATH_NW_EXPORT="/path/to/input/data"
export XL_IDP_ROOT_NW_EXPORT="/path/to/project/root"
export XL_IDP_PATH_DOCKER="/path/to/docker/data"

# ClickHouse подключение
export HOST="clickhouse.example.com"
export DATABASE="database_name"
export USERNAME_DB="username"
export PASSWORD="password"

# API сервис портов
export IP_ADDRESS_CONSIGNMENTS="192.168.1.100"
export PORT="8080"
```

### 📂 Структура директорий

```
${XL_IDP_PATH_NW_EXPORT}/
├── flat_export_nw/              # Входящие файлы для обработки
│   ├── done/                    # Обработанные файлы
│   └── json/                    # Результаты в JSON
└── flat_export_nw_tracking_update/  # Файлы для обновления треккинга
    ├── done/
    └── json/
```

## 🚀 Механика сборки и запуска

### 💻 Локальная разработка

#### 1. 🔧 Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd export_nw_scripts

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### 2. ⚙️ Настройка переменных окружения

```bash
# Создание .env файла
cp .env.example .env
# Редактирование переменных в .env
```

#### 3. ▶️ Ручной запуск скриптов

```bash
# Обработка одного файла
python3 scripts/flat_export_nw.py /path/to/input.xlsx /path/to/output/

# Запуск обработки через bash
./bash_dir/flat_export_nw.sh

# Запуск в режиме демона
./bash_dir/run_export_nw.sh
```

### 🐳 Docker развёртывание

#### 1. 🏗️ Сборка образа

```bash
# Сборка Docker образа
docker build --build-arg XL_IDP_PATH_DOCKER=/app/data -t export-nw-scripts .
```

#### 2. 🚀 Запуск контейнера

```bash
# Запуск с монтированием данных
docker run -d \
  --name export-nw-processor \
  -v /host/data/path:/app/data \
  -v /host/config/.env:/app/.env \
  export-nw-scripts
```

#### 3. ⭐ Docker Compose (рекомендуемый способ)

```yaml
# docker-compose.yml
version: '3.9'
services:
  export_nw:
    container_name: export_nw
    restart: always
    ports:
      - "8098:8098"
    volumes:
      - ${XL_IDP_PATH_NW_EXPORT_SCRIPTS}:${XL_IDP_PATH_DOCKER}
      - ${XL_IDP_ROOT_NW_EXPORT}:${XL_IDP_PATH_NW_EXPORT}
    environment:
      XL_IDP_ROOT_NW_EXPORT: ${XL_IDP_PATH_DOCKER}
      XL_IDP_PATH_NW_EXPORT: ${XL_IDP_PATH_NW_EXPORT}
      IP_ADDRESS_CONSIGNMENTS: ${IP_ADDRESS_CONSIGNMENTS}
      XL_NW_EXPORT: pkt
      TOKEN_TELEGRAM: ${TOKEN_TELEGRAM}
    build:
      context: export_nw
      dockerfile: ./Dockerfile
      args:
        XL_IDP_PATH_DOCKER: ${XL_IDP_PATH_DOCKER}
    command:
      bash -c "sh ${XL_IDP_PATH_DOCKER}/bash_dir/run_export_nw.sh"
    networks:
      - postgres
```

```bash
# Запуск через compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f export-nw

# Остановка
docker-compose down
```

## 📊 Мониторинг и отладка

### 📝 Логирование

Система использует Python logging для отслеживания процессов:
- 🔗 Подключения к ClickHouse
- 🌐 HTTP запросы к API портов
- ❌ Ошибки обработки файлов
- 📈 Статистика обработанных записей

### ✅ Проверка работы

```bash
# Проверка статуса контейнера
docker ps | grep export-nw

# Просмотр логов
docker logs export-nw-processor

# Проверка обработанных файлов
ls -la ${XL_IDP_PATH_NW_EXPORT}/flat_export_nw/done/
ls -la ${XL_IDP_PATH_NW_EXPORT}/flat_export_nw/json/
```

### 🚨 Типичные ошибки

1. **❌ Ошибки подключения к ClickHouse**
   - ✔️ Проверить переменные окружения HOST, DATABASE, USERNAME_DB, PASSWORD
   - ✔️ Убедиться в доступности сервера ClickHouse

2. **🌐 Ошибки API портов**
   - ✔️ Проверить IP_ADDRESS_CONSIGNMENTS и PORT
   - ✔️ Убедиться в доступности микросервиса

3. **📄 Ошибки обработки файлов**
   - ✔️ Файлы с ошибками перемещаются в папку с префиксом "error_"
   - ✔️ Проверить формат входящих Excel файлов

## 📦 Зависимости

### 🐍 Python пакеты

- **📊 pandas, numpy** - обработка данных
- **📗 openpyxl, xlrd** - работа с Excel файлами
- **🔗 clickhouse-connect** - подключение к ClickHouse
- **🌐 requests** - HTTP запросы
- **⚙️ python-dotenv** - управление переменными окружения
- **📊 csvkit** - дополнительные инструменты для CSV

### 💻 Системные требования

- 🐍 Python 3.8+
- 🐳 Docker 20.10+ (для контейнеризации)
- 💻 Bash shell (для автоматизации)
- 🌐 Доступ к сети (для API и ClickHouse)