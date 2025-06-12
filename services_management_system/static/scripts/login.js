$(function () {
    function showAlert(mensaje) {
        return `
        <div class="alert alert-danger" role="alert">
          ${mensaje}
        </div>`;
    }

    function isEmpty(input) {
        return input.val().trim() === "";
    }

    function hasInvalidSymbols(input) {
        const regex = /^[a-zA-Z0-9_\-.@]*$/;
        return !regex.test(input.val());
    }

    $('#formulario').on('submit', function (evento) {
        let withErrors = false;
        $('#box-errors').empty();

        if (isEmpty($('#nick'))) {
            $('#nick').addClass('is-invalid');
            $('#box-errors').append(showAlert('El campo nombre de usuario está vacío.'));
            withErrors = true;
        } else {
            $('#nick').removeClass('is-invalid');
        }

        if (isEmpty($('#passwd'))) {
            $('#passwd').addClass('is-invalid');
            $('#box-errors').append(showAlert('El campo contraseña está vacío.'));
            withErrors = true;
        } else {
            $('#passwd').removeClass('is-invalid');
        }

        if (!withErrors && (hasInvalidSymbols($('#nick')) || hasInvalidSymbols($('#passwd')))) {
            $('#nick').addClass('is-invalid');
            $('#passwd').addClass('is-invalid');
            $('#box-errors').append(showAlert('Nombre de usuario o contraseña incorrectos.'));
            withErrors = true;
        } else {
            $('#nick').removeClass('is-invalid');
            $('#passwd').removeClass('is-invalid');
        }

        if (withErrors) {
            evento.preventDefault();
        }
    });
});
