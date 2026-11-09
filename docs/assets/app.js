/* mcps-ai — mobile nav toggle + copy-to-clipboard for the install command */
(function () {
  "use strict";

  // Mobile navigation
  var toggle = document.getElementById("nav-toggle");
  var mobileNav = document.getElementById("mobile-nav");

  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      var isOpen = !mobileNav.hidden;
      mobileNav.hidden = isOpen;
      toggle.setAttribute("aria-expanded", String(!isOpen));
    });

    // Close the mobile nav when a link is chosen or Escape is pressed
    mobileNav.addEventListener("click", function (event) {
      if (event.target.tagName === "A") {
        mobileNav.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !mobileNav.hidden) {
        mobileNav.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Copy install command
  var copyBtn = document.getElementById("copy-btn");
  var installCommand = document.getElementById("install-command");

  if (copyBtn && installCommand) {
    var defaultLabel = copyBtn.textContent;

    copyBtn.addEventListener("click", function () {
      var text = installCommand.textContent.trim();

      var done = function () {
        copyBtn.textContent = "Copied ✓";
        copyBtn.classList.add("copied");
        window.setTimeout(function () {
          copyBtn.textContent = defaultLabel;
          copyBtn.classList.remove("copied");
        }, 2000);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        // Fallback for older browsers / non-secure contexts
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "absolute";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (e) { /* noop */ }
        document.body.removeChild(ta);
        done();
      }
    });
  }
})();
