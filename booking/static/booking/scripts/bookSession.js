// Depends on "sessionCalendar.js". So make sure to include it before this script

const bookSessionButton = sessionBookingForm.querySelector('.submit-btn');
addOnPostAndOnResponseFuncAttr(bookSessionButton, 'Booking session...')


sessionBookingForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();
    const formData = new FormData(sessionBookingForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    };

    function bookSession(){
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify(data),
        }
        
        bookSessionButton.onPost();
        sessionCalendarEl.onPost();
        fetch(sessionBookingForm.action, options).then((response) => {
            bookSessionButton.onResponse();
            sessionCalendarEl.onResponse();
            if (response.status !== 201) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if(errors){
                        if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                        for (const [fieldName, msg] of Object.entries(errors)){
                            let field = sessionBookingForm.querySelector(`input[name=${fieldName}]`);
                            if(!field){
                                pushNotification("error", msg);
                                continue;
                            }
                            formFieldHasError(field.parentElement, msg);
                        };

                    }else{
                        pushNotification("error", data.detail ?? 'An error occurred!');
                    }
                });
                
            }else{
                response.json().then((data) => {
                    pushNotification("success", data.detail ?? 'Session booked successfully!');
                    hideSessionBookingModal();
                    // Fetch and display new bookings
                    sessionCalendar.fetchEvents();
                });
            }
        });
    };

    mustAcceptTandC(bookSession, null);
};
