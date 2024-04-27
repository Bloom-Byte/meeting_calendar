// Purpose: Contains utility functions used in the project

// Get the URL parameters and store them in a Proxy object
const URLParams = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
});


/**
 * Waits for the given element to be available in the DOM
 * @param {String} selector The CSS selector of the element to wait for
 * @returns {Promise<Element>} The element that was waited for
 */
function waitForElement(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(mutations => {
            if (document.querySelector(selector)) {
                observer.disconnect();
                resolve(document.querySelector(selector));
            }
        });

        // If you get "parameter 1 is not of type 'Node'" error, see https://stackoverflow.com/a/77855838/492336
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
};


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
        }
    }
    return cookieValue;
};


/**
 * Gets the timezone of the client.
 * @returns {string} the timezone of the client
 */
function getClientTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
};


/**
 * Shows a notification using Noty.js
 * @param {string} type The type of notification to show. Can be 'success', 'error', 'warning', 'info'
 * @param {string} text The text to display in the notification
 * @param {number} timeout The duration of the notification in milliseconds
 * @param {boolean} progressBar Whether to show the progress bar or not
 * @param {boolean} hoverPause Whether to pause the timeout when the notification is hovered over
 * @param {string} theme The theme to use for the notification. Available themes are 'mint', 'nest', 'relax', 'sunset', 'metroui', 'semanticui', 'bootstrap-v4'
 * @param {string} layout The layout to use for the notification
 * @param {string[]} closeWith The events that close the notification. Can be 'click', 'button', 'hover', 'backdrop'
 */
function pushNotification(
    type, 
    text, 
    timeout=3000, 
    progressBar=true,
    hoverPause=true,
    theme='semanticui', 
    layout='topRight', 
    closeWith=['click', 'button']
) {
    new Noty({
        type: type,
        text: text,
        timeout: timeout,
        progressBar: progressBar,
        closeWith: closeWith,
        theme: theme,
        layout: layout,
        killer: true,
        pauseOnHover: hoverPause
    }).show();
};


/**
 * Ensures that hyphens in all keys in the given object are changed to underscores
 * @param {object} obj object with possible hyphenated keys
 * @returns {object} The object with underscored keys
 */
function underScoreObjectKeys(obj){
    const newObj = {};
    for (let key in obj){
        newObj[key.replace('-', '_')] = obj[key];
    };
    return newObj;
};


