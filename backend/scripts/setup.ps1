# setup.ps1
# Скрипт для инициализации структуры FastAPI-проекта (Windows/PowerShell)

$folders = @(
    '.\app',
    '.\app\api',
    '.\app\core',
    '.\app\crud',
    '.\app\db',
    '.\app\db\models',
    '.\app\schemas',
    '.\app\utils',
    '.\tests'
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder | Out-Null
    }
}

# Создаем пустые файлы-модули
$files = @(
    '.\app\api\__init__.py',
    '.\app\api\stations.py',
    '.\app\api\clients.py',
    '.\app\api\locations.py',
    '.\app\api\maintenance.py',
    '.\app\api\auth.py',
    '.\app\api\reports.py',
    '.\app\api\ocpp.py',
    '.\app\core\__init__.py',
    '.\app\core\config.py',
    '.\app\core\security.py',
    '.\app\core\deps.py',
    '.\app\crud\__init__.py',
    '.\app\crud\stations.py',
    '.\app\crud\clients.py',
    '.\app\crud\locations.py',
    '.\app\crud\maintenance.py',
    '.\app\crud\users.py',
    '.\app\crud\ocpp.py',
    '.\app\db\__init__.py',
    '.\app\db\base.py',
    '.\app\db\session.py',
    '.\app\db\models\__init__.py',
    '.\app\db\models\station.py',
    '.\app\db\models\client.py',
    '.\app\db\models\location.py',
    '.\app\db\models\maintenance.py',
    '.\app\db\models\user.py',
    '.\app\db\models\ocpp.py',
    '.\app\schemas\__init__.py',
    '.\app\schemas\station.py',
    '.\app\schemas\client.py',
    '.\app\schemas\location.py',
    '.\app\schemas\maintenance.py',
    '.\app\schemas\auth.py',
    '.\app\schemas\report.py',
    '.\app\schemas\ocpp.py',
    '.\app\main.py',
    '.\app\utils\__init__.py'
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
} 