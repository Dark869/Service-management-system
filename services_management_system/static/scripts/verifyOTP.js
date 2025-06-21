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

    const otpCode = $("#codeotp").val().trim();
    const csrftoken = getCookie("csrftoken");

    if (!otpCode) {
      $("#errores2")
        .removeClass("d-none alert-success")
        .addClass("alert-danger");
      $("#listErrors").text("El codigo no puede estar vacío");
      return;
    }

    $.ajax({
      url: "/verify2fa/",
      type: "POST",
      data: { codeotp: otpCode },
      headers: {
        "X-CSRFToken": csrftoken,
      },
      success: function (response) {
        if (response.status === "success") {
          $("#errores2")
            .removeClass("d-none alert-danger")
            .addClass("alert-success");
          $("#listErrors").text("El código fue verificado correctamente.");
          setTimeout(function () {
            window.location.href = response.redirectUrl;
          }, 2000);
        } else {
          $("#errores2")
            .removeClass("d-none alert-success")
            .addClass("alert-danger");
          $("#listErrors").text(response.message);
          setTimeout(function () {
            window.location.href = response.redirectUrl;
          }, 2000);
        }
      },
      error: function () {
        $("#errores2")
          .removeClass("d-none alert-success")
          .addClass("alert-danger");
        $("#listErrors").text(
          "Ocurrió un error al verificar el código. Por favor, intente de nuevo."
        );
      },
    });
  });
});
