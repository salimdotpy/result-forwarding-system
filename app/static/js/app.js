document.addEventListener('htmx:afterRequest', (event) => {
  if (event.detail.successful && event.detail.pathInfo?.requestPath === '/login') {
    window.location.reload();
  }
});
