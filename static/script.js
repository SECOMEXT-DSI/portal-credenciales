document.getElementById('addUserForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);

    fetch('/add_user', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = 'Usuario añadido';
        location.reload();
    })
    .catch((error) => {
        document.getElementById('response').innerText = 'Error: ' + error;
    });
});

function updateStatus(id, valid) {
    fetch('/update_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id, valid: valid ? 1 : 0 }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Estado actualizado');
    })
    .catch((error) => {
        console.log('Error:', error);
    });
}

function updateExpirationDate(id) {
    var expiration_date = document.getElementById('expiration_' + id).value;

    fetch('/update_expiration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id, expiration_date: expiration_date }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = 'Fecha de expiración actualizada';
    })
    .catch((error) => {
        console.log('Error:', error);
    });
}

function deleteUser(id) {
    fetch('/delete_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = 'Usuario eliminado';
        location.reload();
    })
    .catch((error) => {
        console.log('Error:', error);
    });
}