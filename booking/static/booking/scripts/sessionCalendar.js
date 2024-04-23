const sessionCalendarEl = document.querySelector('#session-calendar');
const userTimezone =  document.querySelector('#user-timezone').innerText.trim();

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

const unavailableEventTitle = 'Booked/unavailable';


sessionCalendarEl.onPost = function(){
    this.classList.add('loading');
}

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
};


/**
 * Hides the session edit modal and resets the session edit form fields
 */
function hideSessionEditModal(){
    sessionEditForm.reset();
    sessionEditModal.classList.remove("show-block");
};


/**
 * Converts a time string to a Date object with date provided or today's date, and the time from the time string
 * @param {String} timeStr The time to convert in the format 'HH:MM' 
 * @param {String} dateStr A string representing the date in the format 'YYYY-MM-DD'
 * @returns {Date} A Date object with today's date and the time from the time string
 */
function timeStrToDate(timeStr, dateStr=null){
    let time = timeStr.split(":");
    if (dateStr){
        date = new Date(dateStr);
    }else{
        let date = new Date();
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
 * Checks if a time string is within any of the unavailable time periods
 * @param {String} timeStr  The time to check in the format 'HH:MM'
 * @returns {Boolean} Returns true if the time is within any of the unavailable time periods, otherwise false
 */
function timeIsUnavailable(timeStr, dateStr){
    const callback = (bookingData) => {
        const unavailableTimes = bookingData.unavailable_times;
        for (const range of unavailableTimes){
            let start = range[0];
            let end = range[1];
            start = timeStrToDate(start);
            end = timeStrToDate(end);
            time = timeStrToDate(timeStr);
            if (time >= start && time <= end){
                return true;
            }
        }
        return false;
    };
    return fetchBookingDataForDate(dateStr, callback);
}


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


document.addEventListener('DOMContentLoaded', function() {
    var sessionCalendar = new FullCalendar.Calendar(sessionCalendarEl, {
        themeSystem: 'standard',
        initialView: 'dayGridMonth',
        customButtons: {
            backToMonth: {
                text: 'Back to month',
                click: onBackToMonthClick,
                hint: 'Return to month view',
            },
            viewBookings: {
                text: 'View bookings',
                click: onViewBookingsClick,
                hint: 'View booked sessions',
            },
            edit: {
                text: 'Edit',
                click: onEditClick,
            }
        },
        headerToolbar: {
            left: 'prev,next,viewBookings',
            center: 'title',
            right: 'edit,backToMonth,today'
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
                slotDuration: '00:05:00',
                slotLabelInterval: '00:05',
                eventResizableFromStart: true,
                eventDurationEditable: true,
                eventDrop: onEventDropOrResize,
                eventResize: onEventDropOrResize,
            }   
        },
        timeZone: userTimezone,
        longPressDelay: 250,
        navLinks: false,
        // Shows event details as user selects
        selectMirror: true,
        unselectAuto: true,
        unselectCancel: "#session-booking-modal",
        // User cannot select slots that overlap with existing events
        selectOverlap: false,
        // User cannot select slots occupied by event(sessions)
        dragScroll: true,
        // By default, user cannot edit events
        editable: false,
    });
    sessionCalendar.render();

    // If a date is provided in the URL, navigate to that date
    const preferredDate = URLParams.date ?? null;
    if (preferredDate){
        try{
            navigateToBookingsForDate(preferredDate);
        }catch(err){
            console.error("Invalid date provided in URL");
        };
    };

    // CALLBACKS
    function onDateClick(info){
        const displayUnavailableTimePeriods = (bookingData) => {
            const unavailableTimeRanges = bookingData.unavailable_times;
            showUnavailableTimeslots(unavailableTimeRanges);
            // move to time grid for that day
            sessionCalendar.changeView('timeGridDay', info.dateStr);
            // add time view class, enables custom css when in time view
            sessionCalendarEl.classList.add("in-time-view");
        };

        return fetchBookingDataForDate(info.dateStr, displayUnavailableTimePeriods);
    };


    function onTimeSelect(selectInfo){
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


    // Close edit modal when user clicks outside the modal
    document.addEventListener("click", (e) => {
        if (!sessionEditModal.contains(e.target) && sessionEditModal.classList.contains("show-block")){
            hideSessionEditModal();
        };
    });


    function onBackToMonthClick() {
        sessionCalendar.changeView('dayGridMonth');
        // remove time view class
        sessionCalendarEl.classList.remove("in-time-view");
        const viewBookingsButton = sessionCalendarEl.querySelector('.fc-viewBookings-button');
        // Return view bookings button to default state
        viewBookingsButton.classList.remove('viewing-bookings');
        // Hide booked timeslots
        hideBookedTimeslots();
    };


    function onViewBookingsClick(e){
        const viewBookingButton = e.target;
        viewBookingButton.classList.toggle('viewing-bookings');
        const date = formatDate(sessionCalendar.getDate(), "-");
        const isViewingBookings = viewBookingButton.classList.contains('viewing-bookings');

        if (isViewingBookings){
            console.log("Viewing bookings");
            hideUnavailableTimeslots();
            // Users can only book sessions when not viewing bookings
            sessionCalendar.setOption('selectable', false);

            const displayBookedTimePeriods = (bookingData) => {
                showBookedTimeslots(bookingData.booked_times);
            }
            fetchBookingDataForDate(date, displayBookedTimePeriods);

        }else{
            sessionCalendar.setOption('selectable', true);
            // When exiting bookings view, check if user is editing a session
            // If they are, exit edit mode
            const editButton = sessionCalendarEl.querySelector('.fc-edit-button');
            if (editButton && editButton.classList.contains('editing')){
                editButton.click();
            };

            hideBookedTimeslots();
            const displayUnavailableTimePeriods = (bookingData) => {
                showUnavailableTimeslots(bookingData.unavailable_times);
            }
            fetchBookingDataForDate(date, displayUnavailableTimePeriods);
        }
    };


    function onEditClick(e){
        const editButton = e.target;
        const editable = sessionCalendar.getOption("editable");

        if (editable){
            sessionCalendar.setOption("editable", false);
            editButton.classList.remove("editing");
        }else{
            sessionCalendar.setOption("editable", true);
            editButton.classList.add("editing");
        };
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
            
        // Wait for the unavailable time slots to be displayed
        waitForElement('.unavailable-time-slot').then(() => {
            // Get the viewBookings button and click it to view bookings
            const viewBookingsButton = sessionCalendarEl.querySelector('.fc-viewBookings-button');
            viewBookingsButton.click();
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
        }
    };


    /**
     * Shows booked time periods as events on the calendar
     * @param {Object} bookedTimes An object containing the booked time periods
     */
    function showBookedTimeslots(bookedTimes){
        for (const [sessionCategory, categoryData] of Object.entries(bookedTimes)) {
            for (const [sessionTitle, sessionData] of Object.entries(categoryData)){
                const timeRange = sessionData.time_period
                const date = sessionData.date
                const id = sessionData.id
                const sessionLink = sessionData.link
                const startTime = timeRange[0];
                const endTime = timeRange[1];
                const startDate = date + "T" + startTime;
                const endDate = date + "T" + endTime;
                const classNames = [`session-${sessionCategory}`, "booked-session"];
                if (sessionLink){
                    classNames.push("session-has-url");
                }

                const event = sessionCalendar.addEvent({
                    title: `${sessionTitle} (${sessionCategory})`,
                    start: startDate,
                    end: endDate,
                    display: 'block',
                    selectable: false,
                    overlap: false,
                    classNames: classNames,
                    id: id,
                    extendedProps: {
                        sessionTitle: sessionTitle,
                        type: sessionCategory
                    }
                });
                if (sessionLink){
                    event.setProp('url', sessionLink);
                }
            }
        }
    };


    /**
     * Hides all booked time slots from the calendar
     */
    function hideBookedTimeslots(){
        const events = sessionCalendar.getEvents();
        for (const event of events){
            if (event.classNames.includes('booked-session')){
                event.remove();
            }
        }
    };
});
