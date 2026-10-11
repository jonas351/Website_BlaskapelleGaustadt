(() => {
  function initialize(root = document) {
    root.querySelectorAll('[data-bg-nav]').forEach(nav => {
      if (nav.dataset.initialized) return;
      nav.dataset.initialized = 'true';
      const button = nav.querySelector('button');
      const links = nav.querySelector('.bg-nav-links');
      const close = () => { button.setAttribute('aria-expanded', 'false'); links.classList.remove('is-open'); };
      button.addEventListener('click', () => { const open = button.getAttribute('aria-expanded') !== 'true'; button.setAttribute('aria-expanded', String(open)); links.classList.toggle('is-open', open); });
      nav.addEventListener('keydown', event => { if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { close(); button.focus(); } });
      links.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
      document.addEventListener('click', event => { if (!nav.contains(event.target)) close(); });
      window.matchMedia('(min-width:1025px)').addEventListener('change', close);
    });
    root.querySelectorAll('[data-bg-inquiry]').forEach(container => {
      if (container.dataset.initialized) return;
      container.dataset.initialized = 'true';
      const form = container.querySelector('form');
      const subject = form.querySelector('[name=subject]');
      const query = new URLSearchParams(location.search).get('anliegen');
      if (query === 'auftritt') subject.value = 'Auftrittsanfrage';
      if (query === 'mitmachen') subject.value = 'Mitmachen';
      const status = container.querySelector('[role=status]');
      const fieldset = form.querySelector('fieldset');
      if (fieldset.dataset.configured !== 'yes') return;
      fieldset.disabled = false;
      let sending = false;
      form.addEventListener('submit', async event => {
        event.preventDefault();
        if (sending || !form.reportValidity()) return;
        sending = true;
        const data = new FormData(form);
        fieldset.disabled = true;
        status.textContent = 'Deine Nachricht wird gesendet …';
        status.dataset.state = 'sending';
        try {
          const response = await fetch(container.dataset.endpoint, { method: 'POST', body: data, credentials: 'same-origin' });
          const result = await response.json();
          if (!response.ok || !result.success) {
            const error = new Error(result.data?.message || 'Der Versand hat nicht funktioniert. Bitte nutze den direkten Kontaktweg.');
            error.userMessage = true;
            throw error;
          }
          status.textContent = result.data.message;
          status.dataset.state = 'success';
          form.reset();
        } catch (error) {
          status.textContent = error.userMessage ? error.message : 'Keine Verbindung. Bitte versuche es erneut oder nutze den direkten Kontaktweg.';
          status.dataset.state = 'error';
        } finally {
          fieldset.disabled = false;
          sending = false;
        }
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => initialize()); else initialize();
  // Elementor replaces widget markup during editing; bind the replacement too.
  const editorInitialize = () => {
    if (window.elementorFrontend?.hooks) window.elementorFrontend.hooks.addAction('frontend/element_ready/global', scope => initialize(scope[0]));
  };
  if (window.jQuery) window.jQuery(window).on('elementor/frontend/init', editorInitialize);
  editorInitialize();
})();
