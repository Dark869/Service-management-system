$(function () {
  setInterval(function () {
    $.ajax({
      url: "/monitor/",
      type: "GET",
      data: {
        server_name: $("#name_server").val(),
      },
      success: function (response) {
        for (let serviceName in response.services) {
          let serviceStatus = response.services[serviceName];
          $(".status-" + serviceName).text(serviceStatus);
        }
      },
      error: function (xhr, status, error) {
        console.error("Error al obtener servicios:", error);
      },
    });
  }, 5000);
});
