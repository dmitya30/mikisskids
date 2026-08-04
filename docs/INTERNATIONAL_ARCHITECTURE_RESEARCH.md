# Исследование международной архитектуры

**Статус:** решение принято
**Дата:** 04.08.2026

## Итог исследования

Выбран полный Shopify storefront на `mikisskids.com`.

Причины:

- скорость запуска важнее полного совпадения с VPS-сайтом;
- каталог содержит около 10 SKU;
- Shopify штатно предоставляет каталог, варианты, остатки, Markets,
  корзину, checkout, заказы и возвраты;
- владельцы допускают отличия международного дизайна;
- headless-вариант потребовал бы отдельной разработки frontend-commerce
  слоя и увеличил бы срок примерно на 5–8 рабочих дней;
- Stripe-only потребовал бы собственной логики заказов, остатков,
  fulfillment и административного интерфейса.

Результат:

- полный Shopify — первая реализация;
- VPS + Storefront API — возможный будущий change request;
- Buy Button — не используется как основная архитектура;
- Tilda остаётся только в российском контуре.

Технический staging оценивается в 5–7 рабочих дней. Возможный запуск
разрешённых SKU — в 7–10 рабочих дней без учёта внешних проверок.

## История исследования

### Исправление преждевременной гипотезы

Полный перенос международного storefront на Shopify ранее был предложен
как рекомендация без достаточного сравнения с гибридным вариантом.

Эта рекомендация отозвана как окончательное решение.

На этой стадии Shopify рассматривался как кандидат, а не как утверждённая платформа.

## Исходная гипотеза владельца проекта

- контент и страницы остаются на VPS;
- английская версия размещается в подпапке или на поддомене;
- иностранная платформа предоставляет только checkout/payment contour.

Гипотеза выглядит технически возможной, но должна пройти проверку
каталога, корзины, налогов, доставки, возвратов, webhooks, PCI и KYC.

## Почему русский сайт остаётся референсом

Он уже содержит:

- согласованную визуальную систему;
- собственный характер бренда;
- спокойный tone of voice;
- качественную адаптивную основу;
- продуктовые фотографии и видео;
- страницы бренда и товаров;
- проверенное техническое SEO.

Нет основания автоматически заменять его американским шаблоном.

## Зачем изучаются иностранные магазины

Не для визуального копирования, а для проверки ожидаемой полноты:

- варианты и комплекты;
- размеры и вес;
- возрастные ограничения;
- инструкции;
- product safety;
- доставка и пошлины;
- возвраты;
- гарантия;
- reviews;
- FAQ;
- traceability;
- доступность поддержки.

## Предварительный принцип

Можно сохранить большую часть визуальной и смысловой основы русского
сайта, одновременно адаптируя обязательные и транзакционные блоки.

Окончательная доля прямой локализации определяется после:

- выбора платформы;
- подтверждения рынков;
- получения product compliance;
- получения условий доставки;
- проверки английского copywriting.

## Источники для следующего прохода

- Shopify international domains:
  https://help.shopify.com/en/manual/international/managing-international-domains
- Shopify international SEO:
  https://help.shopify.com/en/manual/markets/seo
- Shopify Payments Poland:
  https://help.shopify.com/en/manual/payments/shopify-payments/supported-countries/poland
- Tilda multilingual store:
  https://tilda.cc/en/answers/a/multilingual-online-store/
- EU distance selling:
  https://europa.eu/youreurope/business/selling-in-eu/selling-goods-services/ecommerce-distance-selling/index_en.htm
- EU GPSR:
  https://eur-lex.europa.eu/EN/legal-content/summary/general-product-safety-regulation-2023.html
- CPSC high chairs:
  https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/High-Chairs
- CPSC CPC:
  https://www.cpsc.gov/Business--Manufacturing/Testing-Certification/Childrens-Product-Certificate
