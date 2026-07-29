# Tilda Webhook и база заказов

**Статус:** развёрнут и проверен реальной оплатой
**Дата:** 29.07.2026

## Назначение

Приложение принимает оплаченные заявки из формы ST100 и сохраняет их
в SQLite. Оно не взаимодействует напрямую с API Т-Банка и не принимает
данные банковских карт.

Источники истины:

- заявка — Tilda;
- списание — личный кабинет Т-Банка;
- кассовый чек — подключённая онлайн-касса.

## Endpoint

    POST https://mikisskids.ru/api/tilda/paid/<WEBHOOK_SECRET>
    Content-Type: application/x-www-form-urlencoded

Реальный URL не сохраняется в Git и не отправляется в публичные чаты.

## Требования к Tilda

В настройках WebHook:

- подключить сервис только к корзине ST100;
- не включать передачу Cookie;
- не подключать webhook к обычным неоплаченным формам;
- оставить отправку данных только после оплаты.

Документация Tilda описывает `tranid` как Lead ID, однако реальный
production payload оплаченной корзины не содержал `tranid`.

Приложение использует `tranid`, затем хеш идентификатора заказа Tilda,
затем хеш `paymentid`. Повторный стабильный идентификатор не создаёт
вторую запись. Payload без стабильного идентификатора получает HTTP 400.

## Локальный запуск

Задать переменные:

    export WEBHOOK_SECRET="$(
      python3 -c         'import secrets; print(secrets.token_urlsafe(32))'
    )"
    export DB_PATH=/tmp/mikisskids-orders.sqlite3
    export PORT=8091

Запустить:

    python3 -m backend.tilda_webhook.app

## Локальный запрос

    curl --fail-with-body       -X POST       -H 'Content-Type: application/x-www-form-urlencoded'       --data-urlencode 'tranid=local-test-1'       --data-urlencode 'formid=form123'       --data-urlencode 'name=Тестовый Покупатель'       --data-urlencode 'phone=+79990000000'       --data-urlencode 'email=test@example.com'       --data-urlencode 'city=Москва'       --data-urlencode 'payment[amount]=35000'       --data-urlencode         'payment[products][0][name]=Стульчик MIKISSKIDS'       "http://127.0.0.1:8091/api/tilda/paid/$WEBHOOK_SECRET"

Повторный запрос с тем же `tranid` также возвращает `OK`, но не создаёт
вторую запись.

Не использовать реальные данные покупателя при локальном тестировании.

## Production-пути

    code:     /var/www/mikiss/data/repos/mikisskids
    env:      /etc/mikisskids/tilda-webhook.env
    database: /var/lib/mikisskids/orders.sqlite3
    backup:   /var/backups/mikisskids/orders
    service:  tilda-webhook.service
    timer:    tilda-webhook-backup.timer

## Ограничения MVP

- локальный статус называется `paid_reported_by_tilda`;
- webhook не заменяет сверку с Т-Банком;
- административной панели нет;
- просмотр БД выполняется только через SSH;
- секрет необходимо сменить при подозрении на раскрытие.

Документация Tilda:

https://help-ru.tilda.cc/forms/webhook

## Состояние production-компонентов

- webhook service: active;
- Nginx route: работает через HTTPS;
- SQLite: инициализирован, integrity check `ok`;
- backup timer: enabled/active;
- тест восстановления: пройден;
- Tilda WebHook: подключён к ST100;
- `test=test`: HTTP 200 без записи;
- восемь unit-тестов: OK;
- реальная оплаченная заявка сохранена в SQLite;
- production-коммит: `83d337f`.

При первой настройке Nginx тестовый URL попал в access log. Секрет был
сразу заменён, записи удалены, после исправления проверено отсутствие
webhook-путей в access/error logs.
