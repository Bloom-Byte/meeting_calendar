// Depends on "sessionCalendar.js". So make sure to include it before this script

const bookSessionButton = sessionBookingForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(bookSessionButton, 'Booking session...')

sessionBookingForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();
    
    function bookSession(){
        const formData = new FormData(sessionBookingForm);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }

        bookSessionButton.onPost();

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify(data),
        }

        fetch(sessionBookingForm.action, options).then((response) => {
            bookSessionButton.onResponse();
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
                    
                    // Since sessions can only be booked in the unavailable time periods view,
                    // Clicking the view bookings button switches to the bookings view, 
                    // where the new booking is fetched and displayed
                    const viewBookingsButton = document.querySelector('button.fc-viewBookings-button');
                    viewBookingsButton.click();
                    hideSessionBookingModal();
                });
            }
        });
    };

    mustAcceptTandC(bookSession);
};
