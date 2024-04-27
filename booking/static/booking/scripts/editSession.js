// Depends on "sessionCalendar.js". So make sure to include it before this script

const editSessionButton = sessionEditForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(editSessionButton, 'Updating info...')

sessionEditForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(sessionEditForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    editSessionButton.onPost();
    sessionCalendarEl.onPost();
    fetch(sessionEditForm.action, options).then((response) => {
        editSessionButton.onResponse();
        sessionCalendarEl.onResponse();
        
        if (!response.ok) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if(errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = sessionEditForm.querySelector(`input[name=${fieldName}]`);
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
                pushNotification("success", data.detail ?? 'Session Info updated successfully!');
                hideSessionEditModal();
            });
        }
    });
};
