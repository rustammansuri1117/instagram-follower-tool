(function () {
  // Navbar background on scroll
  var nav = document.getElementById('mainNav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 40); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Reveal cards as they scroll into view
  var items = document.querySelectorAll('.plan-card, .step-card');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.parentElement.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    items.forEach(function (el) { el.parentElement.classList.add('reveal'); io.observe(el); });
  }

  // Order form validation (server re-validates everything)
  var form = document.getElementById('orderForm');
  if (form) {
    var user = form.querySelector('#instagram_username');
    var mobile = form.querySelector('#mobile_number');
    var userRe = /^(?!\.)(?!.*\.\.)[A-Za-z0-9._]{1,30}$/;
    var mobRe = /^[6-9]\d{9}$/;
    var normMobile = function (v) {
      v = v.replace(/[\s\-()]/g, '');
      if (v.indexOf('+91') === 0) v = v.slice(3);
      else if (/^91\d{10}$/.test(v)) v = v.slice(2);
      else if (/^0\d{10}$/.test(v)) v = v.slice(1);
      return v;
    };
    var check = function () {
      user.setCustomValidity(userRe.test(user.value.trim().replace(/^@/, '')) ? '' : 'invalid');
      mobile.setCustomValidity(mobRe.test(normMobile(mobile.value)) ? '' : 'invalid');
    };
    [user, mobile].forEach(function (el) { el.addEventListener('input', check); });
    form.addEventListener('submit', function (ev) {
      check();
      if (!form.checkValidity()) { ev.preventDefault(); ev.stopPropagation(); }
      form.classList.add('was-validated');
    });
  }

  // Confirm destructive admin actions
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-confirm]');
    if (btn && !window.confirm(btn.getAttribute('data-confirm'))) ev.preventDefault();
  });
})();
