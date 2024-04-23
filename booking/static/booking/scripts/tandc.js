const agreeButton = document.getElementById('tandc-agree');
const disagreeButton = document.getElementById('tandc-disagree');
const tandcModal = document.getElementById('tandc-modal');


/**
 * Show the terms and conditions modal and wait for the user to accept or reject the terms and conditions.
 * Calls the acceptCallback if the user accepts the terms and conditions, and the rejectCallback if the user rejects the terms and conditions.
 * @param {Function} acceptCallback A function to call if the user accepts the terms and conditions
 * @param {Function} rejectCallback A function to call if the user rejects the terms and conditions
 */
function mustAcceptTandC(acceptCallback=null, rejectCallback=null) {
    tandcModal.classList.add('show-flex');

    agreeButton.onclick = () => {
        if (acceptCallback) {
            acceptCallback();
        }
        tandcModal.classList.remove('show-flex');
    };

    disagreeButton.onclick = () => {
        if (rejectCallback) {
            rejectCallback();
        }
        tandcModal.classList.remove('show-flex');
    };
};
