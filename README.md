Информационная система внеаудиторной работы преподавателей и студентов

## Запуск проекта

1. Скопировать файл `backend/.env.example` в `backend/.env`

```bash
cp backend/.env.example backend/.env
```

2. Запустить контейнеры из корня проекта:

```bash
docker compose up --build
```

Backend будет доступен по ссылке `http://localhost:8000`.
Frontend будет доступен по ссылке `http://localhost:8080`.
