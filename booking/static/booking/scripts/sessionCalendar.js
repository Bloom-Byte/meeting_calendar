const sessionCalendarEl = document.querySelector('#session-calendar');
const userTimezone =  document.querySelector('#user-timezone').innerText.trim();
const businessHourStart = document.querySelector("#business-hour-start").innerText.trim();
const businessHourEnd = document.querySelector("#business-hour-end").innerText.trim();

const sessionBookingModal = document.getElementById('session-booking-modal');
const sessionBookingForm = sessionBookingModal.querySelector('#session-booking-form');
const sessionBookingFormDateField = sessionBookingForm.querySelector("#date");
const sessionBookingFormStartTimeField = sessionBookingForm.querySelector("#start-time");
const sessionBookingFormEndTimeField = sessionBookingForm.querySelector("#end-time");

const sessionEditModal = document.getElementById('session-edit-modal');
const sessionEditForm = sessionEditModal.querySelector('#session-edit-form');
const sessionEditFormIDField = sessionEditForm.querySelector("#session-id");
const sessionEditFormTitleField = sessionEditForm.querySelector("#title");
const sessionEditFormDateField = sessionEditForm.querySelector("#date");
const sessionEditFormStartTimeField = sessionEditForm.querySelector("#start-time");
const sessionEditFormEndTimeField = sessionEditForm.querySelector("#end-time");

const unavailableEventTitle = 'Booked/Unavailable';
// Hours of operation for the calendar
const businessHours = {
    startTime: businessHourStart,
    endTime: businessHourEnd
};


// Always call this when ever a request is made on behalf of the calendar
sessionCalendarEl.onPost = function(){
    this.classList.add('loading');
}

// Call this when a response is received
sessionCalendarEl.onResponse = function(){
    this.classList.remove('loading');
}


/**
 * Shows the session booking modal and sets the date, start time and end time fields
 * to the provided values
 * @param {String} date The date in the format 'YYYY-MM-DD'
 * @param {String} startTime The start time in the format 'HH:MM'
 * @param {String} endTime The end time in the format 'HH:MM'
 * @returns {void}
 */
function showSessionBookingModal(date, startTime, endTime){
    sessionBookingFormDateField.value = date;
    sessionBookingFormStartTimeField.value = startTime;
    sessionBookingFormEndTimeField.value = endTime;

    sessionBookingModal.classList.add("show-block");
};


/**
 * Hides the session booking modal and resets the session booking form fields
 */
function hideSessionBookingModal(){
    sessionBookingForm.reset();
    sessionBookingModal.classList.remove("show-block");
    clearFieldErrors(sessionBookingForm);
};


/**
 * Shows the session edit modal and sets the date, start time and end time fields
 * to the provided values
 * @param {String} id The id of the session to edit
 * @param {String} date The date in the format 'YYYY-MM-DD'
 * @param {String} startTime The start time in the format 'HH:MM'
 * @param {String} endTime The end time in the format 'HH:MM'
 * @returns {void}
 */
function showSessionEditModal(sessionId, title, date, startTime, endTime){
    sessionEditFormIDField.value = sessionId;
    sessionEditFormTitleField.value = title;
    sessionEditFormDateField.value = date;
    sessionEditFormStartTimeField.value = startTime;
    sessionEditFormEndTimeField.value = endTime;
    sessionEditForm.querySelector("#session-id").value = sessionId;

    sessionEditModal.classList.add("show-block");

    // Close edit modal when user clicks outside the modal
    document.addEventListener("click", (e) => {
        if (!sessionEditModal.contains(e.target)){
            hideSessionEditModal();
        };
    });
};


/**
 * Hides the session edit modal and resets the session edit form fields
 */
function hideSessionEditModal(){
    sessionEditForm.reset();
    sessionEditModal.classList.remove("show-block");
    clearFieldErrors(sessionEditForm);
};


/**
 * Converts a time string to a Date object with date provided or today's date, and the time from the time string
 * @param {String} timeStr The time to convert in the format 'HH:MM' 
 * @param {String} dateStr A string representing the date in the format 'YYYY-MM-DD'
 * @returns {Date} A Date object with today's date and the time from the time string
 */
function timeStrToDate(timeStr, dateStr=null){
    let time = timeStr.split(":");
    let date;
    if (dateStr){
        date = new Date(dateStr);
    }else{
        date = new Date();
    }
    date.setHours(time[0], time[1], 0, 0);
    return date;
};


/**
 * Formats a Date object to a string in the format 'YYYY'+separator+'MM'+separator+'DD'
 * @param {Date} date The Date object to format 
 * @param {String} separator The separator to use between the year, month and day
 * @returns {String} The formatted date string in the format 'YYYY'+separator+'MM'+separator+'DD'
 */
function formatDate(date, separator="-") {
    var year = date.getFullYear(); // Get the year (YYYY)
    var month = ('0' + (date.getMonth() + 1)).slice(-2); // Get the month (MM) and add leading zero if necessary
    var day = ('0' + date.getDate()).slice(-2); // Get the day (DD) and add leading zero if necessary
    var formattedDate = year + separator + month + separator + day; // Construct the date string in "YYYY-MM-DD" format
    return formattedDate;
};


/**
 * Checks if a time string is in the past relative to the current date
 * @param {String} timeStr The time to check in the format 'HH:MM'
 * @param {String} currentDateStr A string representing the current date in the format 'YYYY-MM-DD'
 * @returns {Boolean} Returns true if the time is in the past, otherwise false
 */
function checkIfTimeIsInThePast(timeStr, currentDateStr=null){
    const dateFromTime = timeStrToDate(timeStr, currentDateStr);
    const dateNow = new Date();
    return dateNow > dateFromTime;
};


/**
 * Checks if a time string is within a time range
 * @param {String} startTimestr Start time in the format 'HH:MM'
 * @param {String} endTimestr End time in the format 'HH:MM'
 * @param {String} timeStr Time to check in the format 'HH:MM'
 * @returns {Boolean} Returns true if the time is within the time range, otherwise false
 */
function isInTimeRange(startTimestr, endTimestr, timeStr){
    const startTime = timeStrToDate(startTimestr);
    const endTime = timeStrToDate(endTimestr);
    const time = timeStrToDate(timeStr);
    return time >= startTime && time <= endTime;
};


/**
 * Checks if a time string is within any of the unavailable time periods
 * @param {String} timeStr  The time to check in the format 'HH:MM'
 * @returns {Boolean} Returns true if the time is within any of the unavailable time periods, otherwise false
 */
function timeIsUnavailable(timeStr, dateStr){
    const callback = (bookingData) => {
        // use let instead of const to allow for redeclaration
        let unavailableTimes = bookingData.unavailable_times;
        for (const range of unavailableTimes){
            let start = range[0];
            let end = range[1];
            let inRange = isInTimeRange(start, end, timeStr);
            if (inRange){
                return true;
            }
        }
        return false;
    };
    return fetchBookingDataForDate(dateStr, callback);
}


function removeNonBusinessHoursTimeSlot(businessHours){
    const slots = sessionCalendarEl.querySelectorAll('td[data-time]');
    for (const slot of slots){
        const slotTime = slot.getAttribute('data-time');
        if (!isInTimeRange(businessHours.startTime, businessHours.endTime, slotTime)){
            slot.parentElement.style.display = "none";
            slot.parentElement.remove();
        };
    };
};


function executeOnPressAndHold(element, execAfterHoldTime, holdTime=2000){
    var mouseTimer;
    function onMouseUp() { 
        //cancel timer when mouse button is released
        if (mouseTimer) clearTimeout(mouseTimer);
    };

    function onMouseDown() { 
        onMouseUp();
        //set timeout to fire the hold time when the user presses mouse button down
        mouseTimer = setTimeout(execAfterHoldTime, holdTime);
    };

    const isTouchDevice = 'ontouchstart' in document.documentElement;
    if (isTouchDevice){
        element.addEventListener("touchstart", onMouseDown);
        element.addEventListener("touchend", onMouseUp);
    }
    else{
        //listen for mouse up event on body, not just the element you originally clicked on
        element.addEventListener("mousedown", onMouseDown);
        document.body.addEventListener("mouseup", onMouseUp);
    }
};


/**
 * Fetches booking data for a specific date and passes it to a callback function
 * The booking data includes unavailable times and booked times
 * @param {String} dateStr A string representing the date in the format 'YYYY-MM-DD'
 * @param {Function} successCallback A callback function to call after the booking data has been fetched successfully
 * The callback function should accept the bookingData object as an argument
 */
function fetchBookingDataForDate(dateStr, successCallback){
    const data = {
        "date": dateStr,
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
    sessionCalendarEl.onPost();

    fetch(window.location.href, options).then((response) => {
        sessionCalendarEl.onResponse();
        if (!response.ok) {
            response.json().then((data) => {
                const errorDetail = data.detail ?? null
                pushNotification("error", errorDetail ?? 'An error occurred!');
            });
            
        }else{
            response.json().then((data) => {
                const responseData = data.data;
                // console.log(responseData);
                return successCallback(responseData);
            });
        };
    });
};


var sessionCalendar = new FullCalendar.Calendar(sessionCalendarEl, {
    themeSystem: 'standard',
    initialView: 'dayGridMonth',
    customButtons: {
        backToMonth: {
            text: 'Back to month',
            click: onBackToMonthClick,
            hint: 'Return to month view',
        },
        exitEditMode: {
            text: 'Exit edit mode',
            click: () => {disableEdit(true);},
            hint: 'Exit edit mode',
        }
    },
    headerToolbar: {
        left: 'prev,next,exitEditMode',
        center: 'title',
        right: 'backToMonth,today'
    },
    buttonText: {
        today: 'Today'
    },
    views: {
        dayGridMonth: {
            titleFormat: { 
                year: 'numeric', 
                month: 'long' 
            },
            // Disallows user from selecting date slots
            selectable: false,
            dateClick: onDateClick
        },
        timeGridDay: {
            titleFormat: { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            },
            // Allows user to select time slots
            selectable: true,
            select: onTimeSelect,
            unselect: onTimeUnselect,
            allDaySlot: false,
            slotDuration: '01:00:00',
            slotLabelInterval: '01:00:00',
            eventResizableFromStart: true,
            eventDurationEditable: true,
            eventDrop: onEventDropOrResize,
            eventResize: onEventDropOrResize,
            viewDidMount: onTimeGridViewMount
        }   
    },
    timeZone: userTimezone,
    longPressDelay: 250,
    navLinks: false,
    // Shows event details as user selects
    selectMirror: true,
    unselectAuto: true,
    unselectCancel: ".booking-modal",
    // User cannot select slots that overlap with existing events
    selectOverlap: false,
    // User cannot select slots occupied by event(sessions)
    dragScroll: true,
    // By default, user cannot edit events
    editable: false
});
sessionCalendar.render();


// Fetches and displays bookings and unavailable time slots for the current view's date
sessionCalendar.fetchEvents = function(){
    const currentView = this.view;
    // Get the date string of the current view in the format 'YYYY-MM-DD'
    const viewDateStr = formatDate(currentView.currentStart, "-");

    const displayBookingsAndUnavailableTimeSlots = (bookingData) => {
        let unavailableTimeRanges = bookingData.unavailable_times;
        let bookings = bookingData.bookings;
        // Hide old bookings and unavailable timeslots, if any
        hideBookings();
        hideUnavailableTimeslots();

        // Show new bookings and unavailable timeslots
        showBookings(bookings);
        showUnavailableTimeslots(unavailableTimeRanges);
    };
    fetchBookingDataForDate(viewDateStr, displayBookingsAndUnavailableTimeSlots);
};


// If a date is provided in the URL, navigate to that date
const preferredDate = URLParams.date ?? null;
const eventID = URLParams.event ?? null;
if (preferredDate){
    try{
        navigateToBookingsForDate(preferredDate);
        // If an event id is provided, scroll the event into view
        if (eventID){
            scrollEventIntoView(eventID);
        };
    }catch(err){
        console.error("Invalid date provided in URL");
    };
};

// CALLBACKS
function onDateClick(info){
    // move to time grid for that day
    sessionCalendar.changeView('timeGridDay', info.dateStr);
    // add time view class, enables custom css when in time view
    sessionCalendarEl.classList.add("in-time-view");
    sessionCalendar.fetchEvents();
};


function onTimeGridViewMount(info){
    // Remove time slot lanes whose time are not in the business hours
    removeNonBusinessHoursTimeSlot(businessHours);
};


function onTimeSelect(selectInfo){
    const inEditMode = sessionCalendar.getOption("editable");
    if (inEditMode){
        // If user is editing a session, do not allow new bookings
        sessionCalendar.unselect();
        return;
    };

    const startTimestr = selectInfo.startStr.split("T")[1];
    const endTimestr = selectInfo.endStr.split("T")[1];
    const dateStr = selectInfo.startStr.split("T")[0];

    if (checkIfTimeIsInThePast(startTimestr, dateStr)){
        pushNotification("warning", "You cannot book a session in the past");
        sessionCalendar.unselect();
        return;
    };
    
    const startIsUnavailable = timeIsUnavailable(startTimestr, dateStr);
    const endIsUnavailable = timeIsUnavailable(endTimestr, dateStr);

    if (startIsUnavailable || endIsUnavailable){
        pushNotification("warning", "You cannot book a session during an unavailable time");
        sessionCalendar.unselect();
        return;
    };
    showSessionBookingModal(dateStr, startTimestr, endTimestr);
};


function onTimeUnselect(selectInfo){
    hideSessionBookingModal();
};


function onEventDropOrResize(info){
    const event = info.event;
    const oldEvent = info.oldEvent;
    const id = oldEvent.id;
    const startTimestr = event.startStr.split("T")[1];
    const endTimestr = event.endStr.split("T")[1];
    const dateStr = event.startStr.split("T")[0];
    const title = oldEvent.extendedProps.sessionTitle;
    const sessionType = event.extendedProps.type;
    
    // Check if the session has already been held
    if (sessionType === "held"){
        pushNotification("warning", "You cannot edit a session that has already been held");
        info.revert();
        return;
    };

    // Check if the session has already been cancelled
    if (sessionType === "cancelled"){
        pushNotification("warning", "You cannot edit a session that has already been cancelled");
        info.revert();
        return;
    };

    if (checkIfTimeIsInThePast(startTimestr, dateStr)){
        pushNotification("warning", "You cannot book a session in the past");
        // revert the event to its original position
        info.revert();
        return;
    };
    
    const startIsUnavailable = timeIsUnavailable(startTimestr, dateStr);
    const endIsUnavailable = timeIsUnavailable(endTimestr, dateStr);

    if (startIsUnavailable || endIsUnavailable){
        pushNotification("warning", "You cannot book a session during an unavailable time");
        // revert the event to its original position
        info.revert();
        return;
    };
    showSessionEditModal(id, title, dateStr, startTimestr, endTimestr);
};


function onBackToMonthClick() {
    sessionCalendar.changeView('dayGridMonth');
    // remove time view class
    sessionCalendarEl.classList.remove("in-time-view");
    // Exit edit mode
    disableEdit()
    // Hide booked timeslots
    hideBookings();
    // Hide unavailable timeslots
    hideUnavailableTimeslots();
};


// HELPER FUNCTIONS
/**
 * Navigates to bookings for the date provided in the URL
 * @param {String} dateStr A string representing the date in the format 'YYYY-MM-DD'
 */
function navigateToBookingsForDate(dateStr){
    dateStr = formatDate(new Date(dateStr), "-");
    // Simulate a date click event by calling the onDateClick function
    onDateClick({dateStr: dateStr});
};


/**
 * Scrolls the event with the given id into view on the calendar
 * @param {String} eventId The id of the event to scroll into view
 */
function scrollEventIntoView(eventId){
    // Wait for the event to be displayed
    waitForElement(`.event-${eventId}`).then(() => {
        const eventEl = document.querySelector(`.event-${eventId}`);
        if (eventEl){
            eventEl.scrollIntoView({behavior: "smooth", block: "center"});
        };
    });
};


/**
 * Shows unavailable time periods as background events on the calendar
 * @param {Array} unavailableTimeRanges An array of arrays containing the start and end times of the unavailable time periods
 */
function showUnavailableTimeslots(unavailableTimeRanges){
    for (const range of unavailableTimeRanges){
        sessionCalendar.addEvent({
            title: unavailableEventTitle,
            startTime: range[0],
            endTime: range[1],
            display: 'background',
            color: 'red',
            selectable: false,
            overlap: false,
            textColor: 'white',
            editable: false,
            classNames: ["unavailable-time-slot"]
        });
    }
};


/**
 * Hides all unavailable time slots from the calendar
 */
function hideUnavailableTimeslots(){
    const events = sessionCalendar.getEvents();
    for (const event of events){
        if (event.classNames.includes('unavailable-time-slot')){
            event.remove();
        }
    };
};


/**
 * Shows bookings as events on the calendar
 * @param {Object} bookedTimes An object containing the bookings
 */
function showBookings(bookedTimes){
    for (const [sessionCategory, categoryData] of Object.entries(bookedTimes)) {
        for (const [sessionId, sessionData] of Object.entries(categoryData)){
            const timeRange = sessionData.time_period
            const date = sessionData.date
            const sessionTitle = sessionData.title
            const sessionLink = sessionData.link
            const startTime = timeRange[0];
            const endTime = timeRange[1];
            const startDate = date + "T" + startTime;
            const endDate = date + "T" + endTime;
            const classNames = [
                `session-${sessionCategory}`, 
                // Unique identifier (class) for each event
                `event-${sessionId}`,
                "booking"
            ];
            if (sessionLink){
                classNames.push("session-has-url");
            }

            const event = sessionCalendar.addEvent({
                title: `${sessionTitle} (${sessionCategory.toUpperCase()})`,
                start: startDate,
                end: endDate,
                display: 'block',
                selectable: false,
                overlap: false,
                classNames: classNames,
                id: sessionId,
                extendedProps: {
                    sessionTitle: sessionTitle,
                    type: sessionCategory
                }
            });

            if (sessionLink){
                event.setProp('url', sessionLink);
            }

            // Wait for the event to be rendered before getting it and adding the press and hold event listener
            waitForElement(`.event-${sessionId}`).then(() => {
                const eventEl = document.querySelector(`.event-${sessionId}`);
                if (eventEl){
                    executeOnPressAndHold(eventEl, enableEdit, 1200);
                    // Add tippy tool tip
                    const toolTipContent = `${sessionTitle}@${startTime}-${endTime} (${sessionCategory.toUpperCase()})`;
                    tippy(eventEl, {
                        content: toolTipContent,
                        placement: 'top',
                        theme: 'light',
                        duration: 200,
                    });
                };
            });
        }
    }
};


/**
 * Hides any booking shown on the calendar
 */
function hideBookings(){
    const events = sessionCalendar.getEvents();
    for (const event of events){
        if (event.classNames.includes('booking')){
            event.remove();
        }
    };
};


/**
 * Enables edit mode on the calendar
 */
function enableEdit(){
    const inEditMode = sessionCalendar.getOption("editable");
    if (!inEditMode){
        // If calendar is not in edit mode, enter edit mode
        sessionCalendarEl.classList.add("edit-mode");
        sessionCalendar.setOption("editable", true);
    };
};


/**
 * Disables edit mode on the calendar
 * @param {Boolean} revert If true, the calendar will revert to its original stat, before entering edit mode
 */
function disableEdit(revert=false){
    const inEditMode = sessionCalendar.getOption("editable");
    if (inEditMode){
        // If calendar is in edit mode, exit edit mode
        sessionCalendarEl.classList.remove("edit-mode");
        sessionCalendar.setOption("editable", false);

        // Revert the calendar to its original state
        if (revert === true){
            sessionCalendar.fetchEvents();
        };
    };
};
