var sessionCalendarEl = document.querySelector('#session-calendar');
const userTimezone =  document.querySelector('#user-timezone').innerText;
var unavailableTimeRanges = [];

sessionCalendarEl.onPost = function(){
    this.classList.add('loading');
}

sessionCalendarEl.onResponse = function(){
    this.classList.remove('loading');
}

function isInUnavailableTimeRanges(startTime, endTime){
    console.log(unavailableTimeRanges);
    for (const range of unavailableTimeRanges){
        let start = range[0];
        let end = range[1];
        start = new Date(start);
        end = new Date(end);
        startTime = new Date(startTime);
        endTime = new Date(endTime);
        if (startTime >= start && endTime <= end){
            return true;
        }
    }
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
    var sessionCalendar = new FullCalendar.Calendar(sessionCalendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridDay'
        },
        views: {
            dayGridMonth: {
                titleFormat: { year: 'numeric', month: 'long' },
                selectable: false,
                dateClick: onDateClick
            },
            timeGridDay: {
                titleFormat: { year: 'numeric', month: 'long', day: 'numeric' },
                selectable: true,
                allDaySlot: false,
                slotDuration: '00:10:00',
                slotLabelInterval: '00:10',
                select: onTimeSelect,
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
                    unavailableTimeRanges = data.data;
                    // move to time grid for that day
                    sessionCalendar.changeView('timeGridDay', info.dateStr);
                });
            }
        });
    
    }

    function onTimeSelect(info){
        const selectStart = info.startStr;
        const selectEnd = info.endStr;
        if (isInUnavailableTimeRanges(selectStart, selectEnd)){
            pushNotification("error", "Selected time is unavailable");
            return;
        }
    }
});
