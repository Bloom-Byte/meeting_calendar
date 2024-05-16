const accountUpdateForm = document.querySelector('#account-update-form');
const accountUpdateFormCard = accountUpdateForm.parentElement;
const accountUpdateButton = accountUpdateForm.querySelector('.submit-btn');
const emailField = accountUpdateForm.querySelector('#email');
const autoSelectTimezoneButton = accountUpdateForm.querySelector('#auto-timezone');
const timezoneField = accountUpdateForm.querySelector('select#timezone');
const accountDeleteButton = document.getElementById("account-delete");
const resendVerificationEmailLink = document.getElementById("resend-verification-email");
var tzSS = $(timezoneField).selectize();
var timezoneSelectize = tzSS[0].selectize;


addOnPostAndOnResponseFuncAttr(accountUpdateButton, 'Saving changes...');


timezoneSelectize.on("change", () => {
    // Dispatch on change event in parent form
    accountUpdateForm.dispatchEvent(new Event("change"));
    // Dispatch on keyup event in parent form
    accountUpdateForm.dispatchEvent(new Event("keyup"));
});

autoSelectTimezoneButton.onclick = function() {
    const timezone = getClientTimezone(); 
    timezoneSelectize.setValue(timezoneSelectize.search(timezone).items[0].id);
};


accountUpdateForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    accountUpdateButton.onPost();
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
            accountUpdateButton.onResponse();
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
            accountUpdateButton.onResponse();
            accountUpdateButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Account updated successfully!');
                const redirectURL  = data.redirect_url ?? null;
                if(!redirectURL) return;
                
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 3000);
            });
        }
    });
};


accountDeleteButton.addEventListener("click", (e) => {
    e.preventDefault();
    // Show an alert asking if they want to proceed
    let response = confirm("Are you sure you want to delete your account? This action cannot be undone.");
    if (!response) return;
    window.location.href = e.target.href;
})


if (resendVerificationEmailLink){
    resendVerificationEmailLink.addEventListener("click", (e) => {
        e.preventDefault();
        resendVerificationEmailLink.disabled = true;
        resendVerificationEmailLink.style.pointerEvents = 'none !important';
    
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
        }
        fetch(e.target.href, options).then((response) => {
            resendVerificationEmailLink.disabled = false;
            resendVerificationEmailLink.style.pointerEvents = 'auto';
            
            if (!response.ok) {
                response.json().then((data) => {
                    pushNotification("error", data.detail ?? 'An error occurred!');
                });
            }else{
                response.json().then((data) => {
                    pushNotification("success", data.detail ?? 'Verification email sent successfully!');
                });
            }
        });
    });    
};
