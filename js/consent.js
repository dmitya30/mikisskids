"use strict";

(() => {
  const COUNTER_ID = 111056887;
  const COOKIE_NAME = "mk_cookie_consent";
  const COOKIE_VERSION = "v1";
  const ACCEPTED = `${COOKIE_VERSION}.accepted`;
  const REJECTED = `${COOKIE_VERSION}.rejected`;
  const COOKIE_MAX_AGE = 31536000;
  const DISABLE_KEY = `disableYaCounter${COUNTER_ID}`;

  let metricaInitialized = false;
  let settingsReturnFocus = null;

  function readCookie() {
    const prefix = `${COOKIE_NAME}=`;

    for (const part of document.cookie.split(";")) {
      const value = part.trim();

      if (value.startsWith(prefix)) {
        return decodeURIComponent(value.slice(prefix.length));
      }
    }

    return "";
  }

  function cookieDomainAttribute() {
    const hostname = window.location.hostname.toLowerCase();

    if (
      hostname === "mikisskids.ru"
      || hostname.endsWith(".mikisskids.ru")
    ) {
      return "; Domain=.mikisskids.ru";
    }

    return "";
  }

  function writeCookie(value) {
    document.cookie = [
      `${COOKIE_NAME}=${encodeURIComponent(value)}`,
      `Max-Age=${COOKIE_MAX_AGE}`,
      "Path=/",
      "SameSite=Lax",
      "Secure"
    ].join("; ") + cookieDomainAttribute();
  }

  function currentConsent() {
    const value = readCookie();

    if (value === ACCEPTED) {
      return "accepted";
    }

    if (value === REJECTED) {
      return "rejected";
    }

    return "unset";
  }

  function prepareMetricaFunction() {
    if (typeof window.ym === "function") {
      return;
    }

    window.ym = function () {
      window.ym.a = window.ym.a || [];
      window.ym.a.push(arguments);
    };

    window.ym.l = Date.now();
  }

  function loadMetrica() {
    if (metricaInitialized || currentConsent() !== "accepted") {
      return;
    }

    metricaInitialized = true;
    window[DISABLE_KEY] = false;

    prepareMetricaFunction();

    if (!document.querySelector("script[data-mikiss-metrica]")) {
      const script = document.createElement("script");

      script.async = true;
      script.src = "https://mc.yandex.ru/metrika/tag.js";
      script.dataset.mikissMetrica = "true";

      document.head.append(script);
    }

    window.ym(COUNTER_ID, "init", {
      clickmap: true,
      trackLinks: true,
      accurateTrackBounce: true,
      webvisor: false
    });
  }

  function clearMetricaStorage() {
    const cookieNames = document.cookie
      .split(";")
      .map((part) => part.trim().split("=")[0])
      .filter((name) => name.startsWith("_ym"));

    for (const name of cookieNames) {
      document.cookie =
        `${name}=; Max-Age=0; Path=/; SameSite=Lax; Secure`;

      if (
        window.location.hostname === "mikisskids.ru"
        || window.location.hostname.endsWith(".mikisskids.ru")
      ) {
        document.cookie =
          `${name}=; Max-Age=0; Path=/; `
          + "Domain=.mikisskids.ru; SameSite=Lax; Secure";
      }
    }

    try {
      for (let index = localStorage.length - 1; index >= 0; index -= 1) {
        const key = localStorage.key(index);

        if (key && key.toLowerCase().includes("_ym")) {
          localStorage.removeItem(key);
        }
      }
    } catch {
      // Storage may be unavailable in restricted browser modes.
    }
  }

  function stopMetrica() {
    window[DISABLE_KEY] = true;

    if (typeof window.ym === "function" && metricaInitialized) {
      try {
        window.ym(COUNTER_ID, "destruct");
      } catch {
        // The counter may still be waiting for the remote script.
      }
    }

    metricaInitialized = false;
    clearMetricaStorage();
  }

  function closeBanner() {
    document.querySelector(".cookie-consent")?.remove();

    if (
      settingsReturnFocus
      && typeof settingsReturnFocus.focus === "function"
    ) {
      settingsReturnFocus.focus();
    }

    settingsReturnFocus = null;
  }

  function applyConsent(value) {
    if (value === "accepted") {
      writeCookie(ACCEPTED);
      closeBanner();
      loadMetrica();
    } else {
      writeCookie(REJECTED);
      stopMetrica();
      closeBanner();
    }

    document.dispatchEvent(
      new CustomEvent("mikiss:consent-change", {
        detail: { value }
      })
    );
  }

  function bannerMarkup(settingsMode) {
    const title = settingsMode
      ? "Настройки cookies"
      : "Мы используем аналитические cookies";

    const text = settingsMode
      ? "Разрешите или запретите Яндекс.Метрику. "
        + "Это не влияет на работу сайта и оформление заказа."
      : "Яндекс.Метрика помогает улучшать сайт "
        + "и оценивать эффективность рекламы.";

    const closeButton = settingsMode
      ? `
        <button
          class="cookie-consent__close"
          type="button"
          data-cookie-close
          aria-label="Закрыть настройки cookies"
        >×</button>
      `
      : "";

    return `
      <section
        class="cookie-consent"
        role="dialog"
        aria-modal="false"
        aria-labelledby="cookie-consent-title"
        aria-describedby="cookie-consent-description"
      >
        <div class="cookie-consent__body">
          ${closeButton}

          <div class="cookie-consent__copy">
            <h2
              class="cookie-consent__title"
              id="cookie-consent-title"
            >${title}</h2>

            <p
              class="cookie-consent__text"
              id="cookie-consent-description"
            >
              ${text}
              <a
                href="https://mikisskids.ru/legal/privacy/#cookies"
              >Подробнее</a>
            </p>
          </div>

          <div class="cookie-consent__actions">
            <button
              class="cookie-consent__button cookie-consent__button--accept"
              type="button"
              data-cookie-accept
            >Принять</button>

            <button
              class="cookie-consent__button cookie-consent__button--reject"
              type="button"
              data-cookie-reject
            >Отказаться</button>
          </div>
        </div>
      </section>
    `;
  }

  function showBanner(settingsMode = false) {
    document.querySelector(".cookie-consent")?.remove();

    const wrapper = document.createElement("div");
    wrapper.innerHTML = bannerMarkup(settingsMode).trim();

    document.body.append(wrapper.firstElementChild);

    document
      .querySelector("[data-cookie-accept]")
      ?.focus();
  }

  function openSettings(trigger = null) {
    settingsReturnFocus = trigger;
    showBanner(true);
  }

  function reachGoal(goal, params = {}, callback = null) {
    const finish =
      typeof callback === "function" ? callback : () => {};

    if (
      currentConsent() !== "accepted"
      || !metricaInitialized
      || typeof window.ym !== "function"
    ) {
      finish();
      return;
    }

    let finished = false;

    const finishOnce = () => {
      if (finished) {
        return;
      }

      finished = true;
      finish();
    };

    window.setTimeout(finishOnce, 700);

    try {
      window.ym(
        COUNTER_ID,
        "reachGoal",
        goal,
        params,
        finishOnce
      );
    } catch {
      finishOnce();
    }
  }

  window.MikissConsent = Object.freeze({
    counterId: COUNTER_ID,
    getState: currentConsent,
    openSettings,
    reachGoal
  });

  window[DISABLE_KEY] = currentConsent() !== "accepted";

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
      return;
    }

    const accept = event.target.closest("[data-cookie-accept]");
    const reject = event.target.closest("[data-cookie-reject]");
    const close = event.target.closest("[data-cookie-close]");
    const settings = event.target.closest("[data-cookie-settings]");

    if (accept) {
      applyConsent("accepted");
      return;
    }

    if (reject) {
      applyConsent("rejected");
      return;
    }

    if (close) {
      closeBanner();
      return;
    }

    if (settings) {
      event.preventDefault();
      openSettings(settings);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape"
      && document.querySelector("[data-cookie-close]")
    ) {
      closeBanner();
    }
  });

  const start = () => {
    const state = currentConsent();

    if (state === "accepted") {
      loadMetrica();
    } else if (state === "unset") {
      showBanner(false);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, {
      once: true
    });
  } else {
    start();
  }
})();
