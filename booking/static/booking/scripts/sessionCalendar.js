var sessionCalendarEl = document.querySelector('#session-calendar');
const userTimezone =  document.querySelector('#user-timezone').innerText;

sessionCalendarEl.onPost = function(){
    this.classList.add('loading');
}

sessionCalendarEl.onResponse = function(){
    this.classList.remove('loading');
}

function timeStrToDate(timeStr){
    let time = timeStr.split(":");
    let date = new Date();
    date.setHours(time[0], time[1], 0, 0);
    return date;
}

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


document.addEventListener('DOMContentLoaded', function() {
    var sessionCalendar = new FullCalendar.Calendar(sessionCalendarEl, {
        initialView: 'dayGridMonth',
        customButtons: {
            backToMonth: {
                text: 'back to month',
                click: () => {
                    sessionCalendar.changeView('dayGridMonth');
                    // remove time view class
                    sessionCalendarEl.classList.remove("in-time-view");
                }
            }
        },
        headerToolbar: {
            left: 'prev,next',
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
        const data = {
            "date": info.dateStr,
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
                    const unavailableTimeRanges = responseData.unavailable_times;
                    for (const range of unavailableTimeRanges){
                        sessionCalendar.addEvent({
                            title: 'Unavailable',
                            startTime: range[0],
                            endTime: range[1],
                            display: 'background',
                            color: 'red',
                            selectable: false,
                            overlap: false,
                            textColor: 'white',
                            editable: false,
                        });
                    }

                    const bookedTimes = responseData.booked_times;
                    // move to time grid for that day
                    sessionCalendar.changeView('timeGridDay', info.dateStr);
                    // add time view class, enables custom css when in time view
                    sessionCalendarEl.classList.add("in-time-view");
                    // disableTimeslotsInUnavailableTimeRanges(unavailableTimeRanges);
                });
            }
        });
    };

    function onTimeSelect(info){
        const selectStart = info.startStr;
        const selectEnd = info.endStr;
        console.log(selectStart, selectEnd)
    };

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
