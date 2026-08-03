# Roadmap V2

**Статус:** draft  
**Дата:** 03.08.2026

## Gate 0 — документация

- синхронизировать статус;
- сохранить гипотезы;
- зафиксировать вопросы;
- исключить преждевременное решение по Shopify.

## Gate 1 — discovery

Результат:

- сведения о продавце и банковском счёте;
- полный товарный master data;
- рынки;
- логистика;
- compliance matrix;
- shortlist платёжных платформ.

Без результата Gate 1 разработка международного checkout не начинается.

## Gate 2 — архитектурное решение

Сравнить:

1. VPS + hosted checkout;
2. VPS + Shopify backend/checkout;
3. полный Shopify.

Критерии:

- юридическая доступность;
- KYC;
- платежи EUR/USD;
- каталог и остатки;
- налоги;
- доставка;
- возвраты;
- SEO;
- CWV;
- аналитика;
- безопасность;
- стоимость разработки;
- стоимость эксплуатации;
- vendor lock-in;
- объём ручной синхронизации.

Результат: ADR в `DECISIONS.md`.

## Stage 1 — российский каталог

Предварительно:

- master data;
- категории;
- `/catalog/`;
- товарные карточки;
- варианты;
- наличие;
- SEO;
- синхронизация с Tilda;
- тесты;
- deploy.

## Stage 2 — международный storefront

Структура зависит от Gate 2.

Общие задачи:

- английская локализация;
- каталог;
- EUR/USD;
- international delivery;
- returns;
- legal pages;
- product safety;
- analytics and consent;
- SEO;
- staging.

## Stage 3 — commerce

- KYC/KYB;
- payment provider;
- taxes;
- shipping zones;
- test orders;
- refunds;
- chargeback process;
- order notifications;
- webhooks;
- operational instructions.

## Stage 4 — launch

- compliance sign-off по каждому SKU;
- QA;
- accessibility;
- CWV;
- security review;
- production launch;
- post-launch monitoring.

## Предварительные сроки

- discovery: 2–4 рабочих дня;
- российский каталог: 4–7 рабочих дней;
- international storefront: 7–12 рабочих дней;
- payments, shipping and QA: 3–5 рабочих дней;
- общая разработка: 15–25 рабочих дней.

Внешние проверки и сертификация в срок разработки не входят.
