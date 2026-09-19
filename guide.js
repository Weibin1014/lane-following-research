document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('pre').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-command';
    button.type = 'button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy command');
    button.addEventListener('click', async () => {
      const command = (block.querySelector('code')?.innerText || block.innerText).trim();
      try {
        await navigator.clipboard.writeText(command);
        button.textContent = 'Copied';
        button.classList.add('copied');
      } catch {
        const range = document.createRange();
        range.selectNodeContents(block.querySelector('code') || block);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = 'Selected';
      }
      window.setTimeout(() => { button.textContent = 'Copy'; button.classList.remove('copied'); }, 1800);
    });
    block.appendChild(button);
  });
});
