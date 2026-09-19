document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.contact-form').forEach(form => {
    const submit = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.form-status');

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!form.reportValidity()) return;

      const originalLabel = submit.innerHTML;
      submit.disabled = true;
      submit.innerHTML = '<span>Sending enquiry…</span><i aria-hidden="true">· · ·</i>';
      status.className = 'form-status is-pending';
      status.textContent = 'Securely sending your message…';

      try {
        const payload = Object.fromEntries(new FormData(form).entries());
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        const result = await response.json().catch(() => ({}));
        const delivered = response.ok && (result.success === true || result.success === 'true');
        if (!delivered) {
          const error = new Error(result.message || `Submission failed (${response.status})`);
          error.userMessage = result.message || 'The form service did not accept the message. Please try again in a few minutes.';
          throw error;
        }

        form.reset();
        status.className = 'form-status is-success';
        status.textContent = 'Thank you. Your enquiry has been sent to Zhang Weibin.';
      } catch (error) {
        status.className = 'form-status is-error';
        status.textContent = error.userMessage || 'The message could not be sent. Please check your connection and try again.';
      } finally {
        submit.disabled = false;
        submit.innerHTML = originalLabel;
      }
    });
  });
});
