# Backend FastAPI для системы управления ЭЗС

## Описание
Бэкенд реализует REST API для управления электрозарядными станциями, клиентами, локациями, обслуживанием, отчетами и OCPP. Используется FastAPI, Neon.tech (PostgreSQL-совместимая облачная БД), JWT-аутентификация.

---

## Установка и запуск (Windows/PowerShell)

### 1. Клонируйте репозиторий и перейдите в папку backend
```powershell
cd .\backend
```

### 2. Установите зависимости
```powershell
pip install -r requirements.txt
```

### 3. Настройте переменные окружения
Создайте файл `.env` в папке backend со следующим содержимым:
```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_HOST=0.0.0.0
APP_PORT=8000
```

- DATABASE_URL — строка подключения к вашей базе данных Neon.tech (PostgreSQL-совместимая)
- JWT_SECRET_KEY — секрет для подписи JWT

### 4. Запуск сервера
```powershell
uvicorn app.main:app --host $env:APP_HOST --port $env:APP_PORT --reload
```

---

## Swagger/OpenAPI
Документация будет доступна по адресу:  
`http://localhost:8000/docs`

---

## Docker (опционально)
Если хотите запускать через Docker, используйте docker-compose (пример будет добавлен позже).

---

## TODO:
- Реализовать все модули API
- Добавить docker-compose.yml
- Добавить тесты
- Описать RBAC для ролей client, operator, admin, superadmin 