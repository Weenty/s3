### Запуск
```shell
docker compose -f .\docker-compose.yaml up --build -d
```

### Роуты
```url
POST localhost:8000/
```
Загрузка изображений

```url
GET localhost:8000/{page}
```
Получение списка изображений по страницам