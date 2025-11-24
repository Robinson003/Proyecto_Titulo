document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: "{% url 'api_events' %}",

        eventClick: function(info) {
            if(confirm("¿Eliminar esta cita?")) {
                fetch(`/api/events/delete/${info.event.id}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": "{{ csrf_token }}",
                        "Content-Type": "application/json"
                    },
                })
                .then(r => r.json())
                .then(data => {
                    if(data.status === "deleted") info.event.remove();
                });
            }
        }
    });

    calendar.render();

    // Crear cita vía formulario
    const form = document.getElementById('create-appointment-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const fd = new FormData(form);

        fetch("{% url 'api_create_event' %}", {
            method: "POST",
            headers: { "X-CSRFToken": "{{ csrf_token }}" },
            body: fd,
            credentials: 'same-origin'  // importante para CSRF
        })
        .then(r => r.json())
        .then(data => {
            if(data.status === "ok") {
                calendar.refetchEvents();  // recarga el calendario
                form.reset();
            } else {
                console.log("Errores al crear cita:", data.errors);
                alert("Error al crear cita: " + JSON.stringify(data.errors));
            }
        });
    });
});
