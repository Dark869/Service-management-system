$(function () {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  $("#formulario").on("submit", function (e) {
    e.preventDefault();

    const email = $("#email").val().trim();
    const password = $("#passwd").val().trim();
    const captcha = $("#g-recaptcha-response").val().trim();
    const csrftoken = getCookie("csrftoken").trim();

    if (!email) {
      $("#boxStatus").text("Error:");
      $("#errores")
        .removeClass("d-none alert-success")
        .addClass("alert-danger");
      $("#listErrors").text("Debes ingresar un correo electrónico.");
      return;
    }

    if (!password) {
      $("#boxStatus").text("Error:");
      $("#errores")
        .removeClass("d-none alert-success")
        .addClass("alert-danger");
      $("#listErrors").text("Debes ingresar una contraseña.");
      return;
    }

    if (!captcha) {
      $("#boxStatus").text("Error:");
      $("#errores")
        .removeClass("d-none alert-success")
        .addClass("alert-danger");
      $("#listErrors").text("Debes completar el captcha.");
      return;
    }

    $.ajax({
      url: "/login/",
      type: "POST",
      data: {
        email: email,
        passwd: password,
        g_recaptcha_response: captcha,
      },
      headers: {
        "X-CSRFToken": csrftoken,
      },
      success: function (response) {
        if (response.status === "success") {
          $("#boxStatus").text("Éxito:");
          $("#errores")
            .removeClass("d-none alert-danger")
            .addClass("alert-success");
          $("#listErrors").text("Inicio de sesión exitoso.");
          setTimeout(function () {
            window.location.href = response.redirectUrl;
          }, 2000);
        } else {
          $("#boxStatus").text("Error:");
          $("#errores")
            .removeClass("d-none alert-success")
            .addClass("alert-danger");
          $("#listErrors").text(response.message);
        }
      },
      error: function () {
        $("#boxStatus").text("Error:");
        $("#errores")
          .removeClass("d-none alert-success")
          .addClass("alert-danger");
        $("#listErrors").text(
          "Ocurrió un error al iniciar sesión. Por favor, inténtalo de nuevo."
        );
      },
    });
  });
});
