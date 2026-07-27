"use strict";

const siteConfig = {
  telegramPersonal: "https://t.me/mikisskids",
  maxPersonal: ""
};

const checkoutBaseUrl = "https://pay.mikisskids.ru/";

function checkoutUrl(product = "") {
  const url = new URL(checkoutBaseUrl);

  if (product) {
    url.searchParams.set("product", product);
  }

  return url.toString();
}

document.addEventListener(
  "click",
  (event) => {
    if (!(event.target instanceof Element)) {
      return;
    }

    const trigger = event.target.closest("[data-open-order]");

    if (!trigger) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();

    window.location.assign(
      checkoutUrl(trigger.dataset.product || "")
    );
  },
  true
);

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
              <span class="menu-toggle-text" aria-hidden="true">
                Меню
              </span>
              <span class="menu-toggle-icon" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
              </span>
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
          <a href="mailto:welcome@mikisskids.ru">
            welcome@mikisskids.ru
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
                <a href="mailto:welcome@mikisskids.ru">
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

customElements.define("site-header", SiteHeader);
customElements.define("site-footer", SiteFooter);

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
