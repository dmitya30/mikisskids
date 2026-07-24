"use strict";

const siteConfig = {
  telegramPersonal: "https://t.me/mikisskinds",
  maxPersonal: ""
};

const page = document.body.dataset.page || "";

const navItems = [
  { key: "chair", href: "chair/", label: "Стульчик" },
  { key: "travel-seat", href: "travel-seat/", label: "Чемодан" },
  { key: "about", href: "about/", label: "О бренде" },
  { key: "delivery", href: "delivery/", label: "Доставка" }
];

function navMarkup(className = "nav-link") {
  return navItems
    .map(
      (item) => `
        <a
          class="${className}"
          href="${item.href}"
          ${page === item.key ? 'aria-current="page"' : ""}
        >${item.label}</a>
      `
    )
    .join("");
}

class SiteHeader extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <a class="skip-link" href="#main">К содержанию</a>

      <header class="site-header site-header--sticky">
        <div class="container header-inner">
          <a class="brand" href="" aria-label="MIKISSKIDS - главная">
            <img
              src="assets/brand/logo-full.svg"
              alt="MIKISSKIDS"
            >
          </a>

          <nav class="desktop-nav" aria-label="Основная навигация">
            ${navMarkup()}
          </nav>

          <div class="header-actions">
            <a class="header-phone" href="tel:+79030107646">
              +7 (903) 010-76-46
            </a>
            <button
              class="button"
              type="button"
              data-open-order
              data-product=""
            >
              Оформить заказ
            </button>
            <button
              class="menu-toggle"
              type="button"
              aria-label="Открыть меню"
              aria-expanded="false"
              aria-controls="mobile-menu"
            >
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </header>

      <div class="mobile-menu" id="mobile-menu">
        <nav aria-label="Мобильная навигация">
          ${navMarkup("")}
        </nav>
        <div class="mobile-menu-contact">
          <a href="tel:+79030107646">+7 (903) 010-76-46</a><br>
          <a href="mailto:ipmalyshevaekaterinasergeevna@yandex.ru">
            ipmalyshevaekaterinasergeevna@yandex.ru
          </a>
        </div>
      </div>
    `;
  }
}

class SiteFooter extends HTMLElement {
  connectedCallback() {
    const telegramMarkup = siteConfig.telegramPersonal
      ? `
        <a
          class="social-link"
          href="${siteConfig.telegramPersonal}"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Написать MIKISSKIDS в Telegram"
        >
          <img
            src="assets/icons/social/telegram.svg"
            alt=""
            aria-hidden="true"
          >
          <span>Telegram</span>
        </a>
      `
      : "";

    const maxMarkup = siteConfig.maxPersonal
      ? `
        <a
          class="social-link"
          href="${siteConfig.maxPersonal}"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Написать MIKISSKIDS в MAX"
        >
          <img
            src="assets/icons/social/max.svg"
            alt=""
            aria-hidden="true"
          >
          <span>MAX</span>
        </a>
      `
      : `
        <span
          class="social-link social-link--disabled"
          aria-label="MAX - ссылка появится позже"
        >
          <img
            src="assets/icons/social/max.svg"
            alt=""
            aria-hidden="true"
          >
          <span>MAX - скоро</span>
        </span>
      `;

    this.innerHTML = `
      <footer class="site-footer">
        <div class="container">
          <div class="footer-grid">
            <div>
              <span class="footer-brand">MIKISSKIDS</span>
              <p class="footer-copy">
                Продуманные предметы высокого класса для дома
                и семейных путешествий.
              </p>

              <div class="social-links" aria-label="Мессенджеры">
                ${telegramMarkup}
                ${maxMarkup}
              </div>
            </div>

            <div>
              <h2 class="footer-title">Разделы</h2>
              <div class="footer-links">
                <a href="chair/">Стульчик</a>
                <a href="travel-seat/">Чемодан</a>
                <a href="about/">О бренде</a>
                <a href="delivery/">Доставка и оплата</a>
              </div>
            </div>

            <div>
              <h2 class="footer-title">Контакты</h2>
              <div class="footer-links">
                <a href="tel:+79030107646">+7 (903) 010-76-46</a>
                <a href="mailto:ipmalyshevaekaterinasergeevna@yandex.ru">
                  Написать на email
                </a>
                <a href="legal/offer/">Публичная оферта</a>
                <a href="legal/privacy/">Персональные данные</a>
                <a href="legal/agreement/">Соглашение</a>
              </div>
            </div>
          </div>

          <div class="footer-bottom">
            <span>
              © ${new Date().getFullYear()} MIKISSKIDS
            </span>
            <span>
              ИП Малышева Екатерина Сергеевна ·
              ИНН 772825786760 · ОГРНИП 323774600756318
            </span>
          </div>
        </div>
      </footer>
    `;
  }
}

class OrderDialog extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <dialog class="order-dialog" aria-labelledby="order-title">
        <div class="dialog-inner">
          <div class="dialog-head">
            <div>
              <p class="eyebrow">MIKISSKIDS</p>
              <h2 id="order-title">Оформить заказ</h2>
            </div>
            <button
              class="icon-button"
              type="button"
              data-close-order
              aria-label="Закрыть"
            >×</button>
          </div>

          <p class="muted" id="order-product-label">
            Выберите товар и оставьте контакты.
          </p>

          <form id="order-form">
            <div class="form-grid">
              <div class="field field--full">
                <label for="product">Товар</label>
                <select id="product" name="product" required>
                  <option value="">Выберите товар</option>
                  <option value="chair">
                    Стульчик-трансформер - 35 000 ₽
                  </option>
                  <option value="travel-seat">
                    Чемодан-кресло - 50 000 ₽
                  </option>
                </select>
              </div>

              <div class="field">
                <label for="name">Имя</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  autocomplete="name"
                  required
                >
              </div>

              <div class="field">
                <label for="phone">Телефон</label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  autocomplete="tel"
                  placeholder="+7"
                  required
                >
              </div>

              <div class="field">
                <label for="email">Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autocomplete="email"
                >
              </div>

              <div class="field">
                <label for="city">Город</label>
                <input
                  id="city"
                  name="city"
                  type="text"
                  autocomplete="address-level2"
                  required
                >
              </div>

              <div class="field field--full">
                <label for="comment">Комментарий</label>
                <textarea
                  id="comment"
                  name="comment"
                  placeholder="Удобное время для связи или вопрос о доставке"
                ></textarea>
              </div>

              <label class="checkbox field--full">
                <input type="checkbox" name="offer" required>
                <span>
                  Я принимаю условия
                  <a href="legal/offer/" target="_blank">
                    публичной оферты
                  </a>.
                </span>
              </label>

              <label class="checkbox field--full">
                <input type="checkbox" name="privacy" required>
                <span>
                  Я даю
                  <a href="legal/consent/" target="_blank">
                    согласие на обработку персональных данных
                  </a>.
                </span>
              </label>
            </div>

            <p class="form-note">
              В прототипе форма не отправляет данные и не переводит
              на страницу оплаты.
            </p>

            <button class="button" type="submit">
              Продолжить
            </button>

            <div class="form-status" role="status" aria-live="polite">
              Интерфейс формы работает. Перед запуском к нему будет
              подключён сервер заказов и платёжная страница Т-Банка.
            </div>
          </form>
        </div>
      </dialog>
    `;
  }
}

customElements.define("site-header", SiteHeader);
customElements.define("site-footer", SiteFooter);
customElements.define("order-dialog", OrderDialog);

const menuButton = document.querySelector(".menu-toggle");
const mobileMenu = document.querySelector(".mobile-menu");

menuButton?.addEventListener("click", () => {
  const isOpen = document.body.classList.toggle("menu-open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
  menuButton.setAttribute(
    "aria-label",
    isOpen ? "Закрыть меню" : "Открыть меню"
  );
});

mobileMenu?.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    document.body.classList.remove("menu-open");
    menuButton?.setAttribute("aria-expanded", "false");
  }
});

const dialog = document.querySelector(".order-dialog");
const productSelect = document.querySelector("#product");
const productLabel = document.querySelector("#order-product-label");
const orderForm = document.querySelector("#order-form");
const formStatus = document.querySelector(".form-status");

const productNames = {
  chair: "Стульчик-трансформер - 35 000 ₽",
  "travel-seat": "Чемодан-кресло - 50 000 ₽"
};

function openOrderDialog(product = "") {
  if (!dialog) return;

  if (productSelect) {
    productSelect.value = productNames[product] ? product : "";
  }

  if (productLabel) {
    productLabel.textContent = productNames[product]
      ? productNames[product]
      : "Выберите товар и оставьте контакты.";
  }

  formStatus?.classList.remove("is-visible");
  dialog.showModal();
  document.body.classList.add("dialog-open");
}

function closeOrderDialog() {
  if (!dialog) return;
  dialog.close();
  document.body.classList.remove("dialog-open");
}

document.addEventListener("click", (event) => {
  const openButton = event.target.closest("[data-open-order]");
  const closeButton = event.target.closest("[data-close-order]");

  if (openButton) {
    openOrderDialog(openButton.dataset.product || "");
  }

  if (closeButton) {
    closeOrderDialog();
  }
});

dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) {
    closeOrderDialog();
  }
});

dialog?.addEventListener("close", () => {
  document.body.classList.remove("dialog-open");
});

orderForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!orderForm.reportValidity()) return;

  formStatus?.classList.add("is-visible");
});

const revealObserver =
  "IntersectionObserver" in window
    ? new IntersectionObserver(
        (entries, observer) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          });
        },
        { threshold: 0.12 }
      )
    : null;

document.querySelectorAll(".reveal").forEach((element) => {
  if (revealObserver) {
    revealObserver.observe(element);
  } else {
    element.classList.add("is-visible");
  }
});


const ambientVideos = document.querySelectorAll("[data-ambient-video]");
const reducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
);

function syncAmbientVideos() {
  ambientVideos.forEach((video) => {
    video.muted = true;

    if (reducedMotion.matches || document.hidden) {
      video.pause();
      return;
    }

    video.play().catch(() => {
      // The poster remains visible when a browser blocks autoplay.
    });
  });
}

syncAmbientVideos();
document.addEventListener("visibilitychange", syncAmbientVideos);
reducedMotion.addEventListener?.("change", syncAmbientVideos);
