# Архитектура MIKISSKIDS

**Статус:** российская архитектура актуальна; международная исследуется
**Дата:** 03.08.2026

## Компоненты

### Основной сайт

- статические HTML, CSS и JavaScript;
- production на российском VPS;
- Nginx;
- домены `mikisskids.ru` и `www.mikisskids.ru`;
- `www` перенаправляется на основной домен;
- HTTPS обязателен.

### Платёжная страница

- поддомен `pay.mikisskids.ru`;
- проект Tilda;
- корзина ST100;
- готовая интеграция Tilda с Т-Банком;
- одностадийная оплата;
- Return URL:
  `https://pay.mikisskids.ru/payment-success`;
- опубликованы только checkout `payment-mvp`, назначенный главной
  страницей поддомена, и `payment-success`;
- устаревшие страницы Tilda сняты с публикации;
- обе опубликованные страницы закрыты от индексации;
- URL-цель `/payment-success` используется для оценки конверсии,
  а не как финансовый источник истины.

Собственные API-запросы к Т-Банку и серверное событие Метрики
на текущем этапе не реализуются. Terminal ID, пароль
терминала и реквизиты карт не хранятся в репозитории или приложении VPS.

### Хранилище заказов

VPS принимает копию оплаченной заявки через Tilda Webhook и сохраняет
её в SQLite.

```text
Tilda ST100
    → оплата через Т-Банк
    → успешная оплата
    → Tilda Webhook
    → Nginx
    → локальное webhook-приложение
    → SQLite
```

Webhook Tilda является источником сведений для операционного учёта,
а кабинет Т-Банка и касса остаются источниками истины по оплате и чеку.

## Идентификатор заказа

Приоритет стабильного идентификатора:

1. `tranid`, если присутствует;
2. хеш идентификатора заказа Tilda;
3. хеш `paymentid`.

Резервные идентификаторы хешируются SHA-256 с префиксом типа.
Уникальное ограничение SQLite обеспечивает идемпотентность. Payload
без стабильного идентификатора отклоняется с HTTP 400.

## Минимальные данные заказа

- стабильный идентификатор заказа;
- дата получения;
- товар;
- сумма;
- имя;
- телефон;
- email;
- город;
- комментарий;
- источник;
- статус `paid_reported_by_tilda`;
- исходный URL-decoded payload.

Полные реквизиты карты не принимаются и не сохраняются.

## Безопасность

- секретный путь webhook хранится в `.env`;
- база находится вне web root;
- размер запроса ограничен;
- принимаются только POST и form-urlencoded;
- повторный стабильный идентификатор не создаёт новый заказ;
- персональные данные не записываются в access/error logs;
- SQLite и резервные копии имеют права только для service user;
- webhook слушает только loopback, внешний доступ идёт через Nginx;
- endpoint не добавляется в публичную документацию с реальным секретом.

## DNS и размещение

- основной домен направлен на VPS через FASTVPS DNS;
- `www` перенаправляется на основной домен;
- `pay.mikisskids.ru` направлен на Tilda;
- HTTPS работает для основного сайта и платёжного поддомена;
- MX, SPF и DKIM Яндекса сохранены;
- DMARC опубликован в режиме наблюдения `p=none`.

## Деплой

Канонический поток изменений:

```text
локальный Git
    → GitHub main
    → репозиторий VPS
    → sudo /usr/local/sbin/deploy-mikisskids
```

Deploy-скрипт получает `origin/main`, создаёт backup webroot,
синхронизирует публичные файлы, исключает приватные каталоги backend,
deploy, docs и scripts, выполняет `nginx -t` и production smoke-check.

Изменения backend требуют обновления репозитория VPS и перезапуска
соответствующего systemd-сервиса. Документационные коммиты не требуют
публикации в production webroot.
## Обновление российского контура от 03.08.2026

Российская архитектура сохраняется:

```text
mikisskids.ru на VPS
    → pay.mikisskids.ru на Tilda
    → Tilda ST100
    → Т-Банк
    → Tilda webhook
    → Nginx
    → tilda-webhook.service
    → SQLite
```

Каноническая Nginx-конфигурация хранится в:

```text
deploy/nginx-site.conf
```

Устанавливается скриптом:

```text
deploy/install-nginx-site-config
```

Скрипт создаёт backup, выполняет `nginx -t`, reload и проверяет
webhook route.

Production include нельзя заменять отдельным частичным фрагментом.
Такая замена ранее удалила webhook location и вызвала HTTP 404.

SQLite является внутренней копией заявок и не является банковской,
бухгалтерской или фискальной системой.

## Международная архитектура — discovery

Окончательное решение не принято.

### Вариант A — VPS storefront + hosted checkout

```text
international storefront on VPS
    → external hosted checkout
    → payment provider
```

Проверить:

- передачу корзины и вариантов;
- каталог и остатки;
- EUR/USD;
- налоги;
- доставку;
- refunds;
- webhooks;
- PCI scope;
- KYC;
- order management;
- ручную синхронизацию.

### Вариант B — VPS storefront + Shopify commerce backend

```text
international storefront on VPS
    → Shopify Storefront API / supported sales channel
    → Shopify cart and checkout
    → Shopify Payments or supported provider
```

Проверить:

- Buy Button;
- Storefront API;
- headless limitations;
- Shopify Markets;
- checkout branding;
- inventory;
- translations;
- webhooks;
- fees;
- объём собственной разработки;
- стоимость дальнейшего сопровождения.

### Вариант C — полный Shopify storefront

```text
international domain
    → Shopify storefront
    → Shopify Markets
    → Shopify checkout
    → payment provider
```

Проверить:

- перенос фирменного дизайна;
- SEO;
- CWV;
- темы и приложения;
- ограничения checkout;
- владение данными;
- vendor lock-in;
- стоимость эксплуатации;
- необходимость отказа от VPS для международной части.

## Международные URL

Кандидаты:

- `mikisskids.com`;
- `en.mikisskids.ru`;
- `mikisskids.ru/en/`;
- отдельный международный домен.

Выбор зависит от продавца, рынков, SEO, платежей и возможных
юрисдикционных ограничений.

Полный переход storefront на Shopify не утверждён.
