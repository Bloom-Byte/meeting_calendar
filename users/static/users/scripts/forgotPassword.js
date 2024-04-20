const forgotPasswordForm = document.querySelector('#forgot-password-form');
const forgotPasswordFormCard = forgotPasswordForm.parentElement;
const requestResetButton = forgotPasswordForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(requestResetButton, 'Processing request...');

forgotPasswordForm.addEventListener('keyup', function(e) {
    requestResetButton.disabled = false;
});

forgotPasswordForm.addEventListener('change', function(e) {
    requestResetButton.disabled = false;
});


forgotPasswordForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    requestResetButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(this.action, options).then((response) => {
        if (!response.ok) {
            requestResetButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    console.log(errors )
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? 'An error occurred!');
                };
            });

        }else{
            requestResetButton.onResponse();
            requestResetButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Request successful!');
            });
            
            const redirectURL  = data.redirect_url ?? null
            if(!redirectURL) return;
            window.location.href = redirectURL;
        }
    });
};

