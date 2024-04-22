const resetPasswordForm = document.querySelector('#reset-password-form');
const resetPasswordFormCard = resetPasswordForm.parentElement;
const resetPasswordButton = resetPasswordForm.querySelector('.submit-btn');
const passwordField1 = resetPasswordForm.querySelector('#new-password1');
const passwordField2 = resetPasswordForm.querySelector('#new-password2');


addOnPostAndOnResponseFuncAttr(resetPasswordButton, 'Attempting password reset...');

resetPasswordForm.addEventListener('keyup', function(e) {
    resetPasswordButton.disabled = false;
});

resetPasswordForm.addEventListener('change', function(e) {
    resetPasswordButton.disabled = false;
});


resetPasswordForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!validatePassword(passwordField1, passwordField2)) return;

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    resetPasswordButton.onPost();
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
            resetPasswordButton.onResponse();
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
            resetPasswordButton.onResponse();
            resetPasswordButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Password reset successful!');
            });

            const redirectURL  = data.redirect_url ?? null
            if(!redirectURL) return;
            window.location.href = redirectURL;
        }
    });
};

