# Meeting Calendar

## Quick Setup Guide

- Clone the repository

- Change directory to the repository

- Install the requirements using `pip install -r requirements.txt`

- Copy the config in temp.env to a new file called .env and update the values

- Run migrations using `python manage.py migrate`

- Collect staticfiles using `python manage.py collectstatic`

- Create a superuser using `python manage.py createsuperuser`

- Run the server using `python manage.py runserver`

## How things work

The project is an app where users can book a session and view the meetings they have booked. The admin can view all the booked sessions and add links for users to join the meeting when the time comes.

> NOTE: All the time displayed in the app is always in the user's timezone. All bookings are also done in the user's timezone.

### User Registration and Authentication

- Users can sign up by providing their email, first name, last name, and password. The email is used as the username.
The user's timezone info is automatically detected and stored in the user's profile on sign up.
- Users can log in using their email and password.
- Users can reset their password by providing their email on the forgot password page.

### User Dashboard

- On logging in, users are redirected to their dashboard where they can see session that they have booked for that day.

> The time displayed is in the user's timezone.

- User can also see news and updates from the admin for that day, if any.
- Users can then proceed to book a session by clicking on the calendar icon on the sidebar.

### Booking a Session

- To book a session on the calendar page, users can click on the date they want to book a meeting for. On clicking the date, the calendar switches to the view where they can select the time slot they want to book.

- In the time slot view, users can see the unavailable time slots for that day. They are highlighted in red. Users can only book a meeting for a time slot that is available.

- The time slots are in durations of 5 minutes.

- To select a time slot, long press on the time slot for about 2 seconds until the time slot is highlight in blue. You can then drag the time slot to the duration you want. The time period is displayed on the blue box that appears.

- After selecting the time slot, a modal appears where the user can enter the meeting title and confirm that the details of the booking are correct. If they are not, you can tap outside the modal and it will close for you reselect the timeslot again.

- After confirming the details, the user can click on the book button to book the meeting. The user is required to accept the terms of service which wil be displayed on clicking the book button. The user can then click on the accept button to book the meeting. Not accepting the terms of service will not allow the user to book the meeting.

- A success notification is displayed on successful booking of the meeting. Else, a notification is displayed with the a reason why the booking failed.

### Viewing Booked Sessions

Users can view their booked sessions by navigating to the calendar page and clicking on the day they booked the session for. On the top-left corner of the calendar page, there is a button that says "View bookings". Clicking on this button will display the sessions that the user has booked as events on the calendar. Clicking this button again will hide the sessions.

### Editing or Rescheduling a Session

Navigate to the view where you can see the sessions you have booked as events (as described in the last section). Click on the edit button on the top-right corner of the calendar. This will switch the calendar to the edit mode where you can edit or reschedule any session event displayed on the calendar.

To edit a session, tap and hold on the session for about 2 seconds until the session is highlighted. You can then drag the session to the new time slot you want or change the duration by resizing the event.

### The Settings Page

Users can view and edit their profile information on the settings page. They can also change their password on this page.
There are two forms displayed on the settings page. The first form is for updating the user's profile information. The second form is for changing the user's password.

### The Admin Dashboard
