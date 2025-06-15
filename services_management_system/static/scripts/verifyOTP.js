$(function () {
  function timerRenewOTP() {
    let timeOut = 60;

    const intervalID = setInterval(function () {
      if (timeOut === 0) {
        $("#btnNewCode").prop("disabled", false);
        $("#timerRenewOTP").addClass("d-none");
        $("#textTimer").addClass("d-none");
        $("#btnNewCode").removeClass("btn-secondary").addClass("btn-primary");
        clearInterval(intervalID);
      } else {
        timeOut--;
        $("#timerRenewOTP").text(formatTime(timeOut));
      }
    }, 1000);
  }

  function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec.toString().padStart(2, "0")}`;
  }

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

  $("#btnNewCode").on("click", function () {
    $.ajax({
      url: "/renew2fa/",
      type: "GET",
      success: function (response) {
        if (response.status === "success") {
          $("#timerRenewOTP").text("1:00");
          $("#btnNewCode").prop("disabled", true);
          $("#timerRenewOTP").removeClass("d-none");
          $("#textTimer").removeClass("d-none");
          $("#btnNewCode").removeClass("btn-primary").addClass("btn-secondary");
          timerRenewOTP();
        } else {
          $("#listErrors").text(
            "Ocurrio un error al renovar el OTP. Por favor, intente de nuevo."
          );
        }
      },
      error: function () {
        $("#listErrors").text(
          "Ocurrio un error al renovar el codigo. Por favor, intente de nuevo."
        );
        $("#errores2").removeClass("d-none");
      },
    });
  });

  $("#formulario").on("submit", function (e) {
    e.preventDefault();
    const otpCode = $("#codeotp").val();
    const csrftoken = getCookie("csrftoken");
    $.ajax({
      url: "/registerServer/",
      type: "POST",
      data: { codeotp: otpCode },
      headers: {
        "X-CSRFToken": csrftoken,
      },
      success: function (response) {
        if (response.status === "success") {
          $("#errores2")
            .removeClass("d-none")
            .removeClass("alert-danger")
            .addClass("alert-success");
          $("#listErrors").text("El codigo fue verificado correctamente.");
          setTimeout(function () {
            window.location.href = response.redirectUrl;
          }, 3000);
        } else {
          $("#errores2")
            .removeClass("d-none")
            .removeClass("alert-success")
            .addClass("alert-danger");
          $("#listErrors").text(response.message);
        }
      },
      error: function () {
        $("#listErrors").text(
          "Ocurrio un error al verificar el codigo. Por favor, intente de nuevo."
        );
        $("#errores2").removeClass("d-none");
      },
    });
  });

  timerRenewOTP();
});
