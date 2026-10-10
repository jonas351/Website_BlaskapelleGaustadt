(() => {
  const button = document.querySelector('#team-bamberg-import');
  const status = document.querySelector('#team-bamberg-progress');
  if (!button || !status) return;
  button.addEventListener('click', async () => {
    button.disabled = true;
    status.textContent = 'Import startet … bitte dieses Fenster geöffnet lassen.';
    try {
      for (;;) {
        const body = new URLSearchParams({ action: 'team_bamberg_import', nonce: button.dataset.nonce });
        const response = await fetch(button.dataset.url, { method: 'POST', credentials: 'same-origin', body });
        const result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.data?.message || 'Import konnte nicht abgeschlossen werden.');
        status.textContent = result.data.message;
        if (result.data.done) { window.location.reload(); return; }
      }
    } catch (error) {
      status.textContent = `${error.message} Du kannst den Import erneut starten; bereits angelegte Inhalte bleiben erhalten.`;
      button.disabled = false;
    }
  });
})();
