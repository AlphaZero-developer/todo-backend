@echo off
chcp 65001 >nul
cd /d "%~dp0"

where docker >nul 2>nul || (
    echo [!] Docker не найден. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker info >nul 2>nul || (
    echo [!] Docker Desktop не запущен. Запустите его, дождитесь зелёного статуса и попробуйте снова.
    pause
    exit /b 1
)

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo [i] Создан файл .env из .env.example. Пароль базы можно поменять в нём.
)

echo [i] Собираю и запускаю контейнеры...
docker compose up -d --build || (
    echo [!] docker compose завершился с ошибкой. Логи: docker compose logs
    pause
    exit /b 1
)

echo [i] Жду, пока API ответит...
powershell -NoProfile -Command "for($i=0;$i -lt 60;$i++){try{Invoke-WebRequest http://127.0.0.1:8080/docs -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0}catch{Start-Sleep 1}}; exit 1" || (
    echo [!] API не ответило за минуту. Смотрите логи: docker compose logs todo-backend
    docker compose ps -a
    pause
    exit /b 1
)

echo.
echo [ok] Всё запущено:
echo      API и Swagger:  http://localhost:8080/docs
echo      PostgreSQL:     localhost:5432
echo      Redis:          localhost:6379
echo      Остановить:     docker compose down
echo.
if /i not "%~1"=="--no-browser" start "" "http://localhost:8080/docs"
pause
