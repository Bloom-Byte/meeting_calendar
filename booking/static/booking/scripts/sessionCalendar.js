const sessionCalendarEl = document.querySelector('#session-calendar');
const userTimezone =  document.querySelector('#user-timezone').innerText;
const unavailableEventTitle = 'Booked and unavailable';

sessionCalendarEl.onPost = function(){
    this.classList.add('loading');
}

sessionCalendarEl.onResponse = function(){
    this.classList.remove('loading');
}

/**
 * Converts a time string to a Date object with today's date and the time from the time string
 * @param {String} timeStr The time to convert in the format 'HH:MM' 
 * @returns {Date} A Date object with today's date and the time from the time string
 */
function timeStrToDate(timeStr){
    let time = timeStr.split(":");
    let date = new Date();
    date.setHours(time[0], time[1], 0, 0);
    return date;
}


/**
 * Checks if a time string is within any of the unavailable time ranges
 * @param {String} timeStr  The time to check in the format 'HH:MM'
 * @param {Array[Array]} unavailableTimeRanges An array of arrays containing the start and end times of the unavailable time ranges
 * @returns {Boolean} Returns true if the time is within any of the unavailable time ranges, otherwise false
 */
function isInUnavailableTimeRanges(timeStr, unavailableTimeRanges){
    for (const range of unavailableTimeRanges){
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
                if (successCallback){
                    successCallback(responseData);
                }
            });
        };
    });
};


document.addEventListener('DOMContentLoaded', function() {
    var sessionCalendar = new FullCalendar.Calendar(sessionCalendarEl, {
        initialView: 'dayGridMonth',
        customButtons: {
            backToMonth: {
                text: 'Back to month',
                click: onBackToMonthClick
            },
            viewBookings: {
                text: 'View bookings',
                click: onViewBookingsClick
            }
        },
        headerToolbar: {
            left: 'prev,next,viewBookings',
            center: 'title',
            right: 'backToMonth,today'
        },
        views: {
            dayGridMonth: {
                titleFormat: { 
                    year: 'numeric', 
                    month: 'long' 
                },
                selectable: false,
                dateClick: onDateClick
            },
            timeGridDay: {
                titleFormat: { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                },
                selectable: true,
                select: onTimeSelect,
                allDaySlot: false,
                slotDuration: '00:05:00',
                slotLabelInterval: '00:05',
            }   
        },
    });
    sessionCalendar.render();

    function onDateClick(info){
        const displayUnavailableTimePeriods = (bookingData) => {
            const unavailableTimeRanges = bookingData.unavailable_times;
            showUnavailableTimeslots(unavailableTimeRanges);
            // move to time grid for that day
            sessionCalendar.changeView('timeGridDay', info.dateStr);
            // add time view class, enables custom css when in time view
            sessionCalendarEl.classList.add("in-time-view");
        };

        fetchBookingDataForDate(info.dateStr, displayUnavailableTimePeriods);
    };

    // CALLBACKS
    function onTimeSelect(info){
        const selectStart = info.startStr;
        const selectEnd = info.endStr;
        console.log(selectStart, selectEnd)
    };

    function onBackToMonthClick() {
        sessionCalendar.changeView('dayGridMonth');
        // remove time view class
        sessionCalendarEl.classList.remove("in-time-view");
        const viewBookingsButton = sessionCalendarEl.querySelector('.fc-viewBookings-button');
        viewBookingsButton.classList.remove('viewing-bookings');
    }

    function onViewBookingsClick(e){
        const viewBookingButton = e.target;
        viewBookingButton.classList.toggle('viewing-bookings');
        const date = sessionCalendar.getDate().toISOString().split('T')[0];

        if (viewBookingButton.classList.contains('viewing-bookings')){
            const displayBookedTimePeriods = (bookingData) => {
                showBookedTimeslots(bookingData.booked_times);
            }
            fetchBookingDataForDate(date, displayBookedTimePeriods);
            hideUnavailableTimeslots();

        }else{
            hideBookedTimeslots();
            const displayUnavailableTimePeriods = (bookingData) => {
                showUnavailableTimeslots(bookingData.unavailable_times);
            }
            fetchBookingDataForDate(date, displayUnavailableTimePeriods);
        }
    };


    // HELPER FUNCTIONS
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

    function hideUnavailableTimeslots(){
        const events = sessionCalendar.getEvents();
        for (const event of events){
            if (event.classNames.includes('unavailable-time-slot')){
                event.remove();
            }
        }
    };

    function showBookedTimeslots(bookedTimes){
        for (const [sessionCategory, categoryData] of Object.entries(bookedTimes)) {
            for (const [sessionTitle, timeRange] of Object.entries(categoryData)){
                const startTime = timeRange[0];
                const endTime = timeRange[1];
                const classNames = [`session-${sessionCategory}`, "booked-session"];

                sessionCalendar.addEvent({
                    title: `${sessionTitle} (${sessionCategory})`,
                    startTime: startTime,
                    endTime: endTime,
                    startRecur: startTime,
                    endRecur: endTime,
                    display: 'block',
                    selectable: false,
                    overlap: false,
                    classNames: classNames,
                });
            }
        }
    };

    function hideBookedTimeslots(){
        const events = sessionCalendar.getEvents();
        for (const event of events){
            if (event.classNames.includes('booked-session')){
                event.remove();
            }
        }
    }

    function disableTimeslotsInUnavailableTimeRanges(unavailableTimeRanges){
        const timeGridSlotsContainer = sessionCalendarEl.querySelector('.fc-timegrid-slots');
        const timeGridSlots = timeGridSlotsContainer.querySelectorAll('.fc-timegrid-slot-lane');
        for (const slot of timeGridSlots){
            const slotTime = slot.getAttribute('data-time');
            if (isInUnavailableTimeRanges(slotTime, unavailableTimeRanges)){
                slot.classList.add('unavailable-time-slot');
                slot.innerHTML = "Unavailable";
            }
        }
    }
});
