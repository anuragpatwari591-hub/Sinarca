document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }

  document.querySelectorAll(".flash-stack .alert").forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity .4s ease";
      alert.style.opacity = "0";
      setTimeout(function () { alert.remove(); }, 400);
    }, 5000);
  });

  var chatWindow = document.querySelector(".chat-window");
  if (chatWindow) {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
});
