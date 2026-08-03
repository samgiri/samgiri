document.querySelectorAll('a[target="_blank"]').forEach((link) => {
  link.rel = 'noopener noreferrer';
});

document.querySelectorAll('a[title]').forEach((link) => {
  if (!link.getAttribute('aria-label')) link.setAttribute('aria-label', link.title);
});
