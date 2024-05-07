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

> This project uses sqlite as the database.

**Get directions on how to deploy [here](docker-deploy.md)**

## How things work

The project is an app where you can book a session and view the meetings you have booked. The admin can view all the booked sessions and add links for you to join the meeting when the time comes.

> NOTE: All the time displayed in the app is always in the user's timezone. All bookings are also done in the user's timezone.

### User Registration and Authentication

- You can sign up by providing your email, first name, last name, and password. Your email is used as the username. Also, your timezone info is automatically detected and stored alongside your profile on sign up.
- Make sure to verify your email as a verification mail will be sent on completing sign up.
- You can log in using your email and password.
- You can reset your password by navigating to the forgot password page from the sign up page, and providing your account email.

### User Dashboard

- On logging in, you are redirected to the dashboard where you can see cards showing the sessions that you have booked for that day, if any. These cards contains links to join the meeting when the time comes (If available) or to reschedule the meeting.

> The time displayed is in the user's timezone.

- You can also see news and updates from the admin for that day just below the session, if any.
- You can then proceed to book a session by clicking on the calendar icon on the sidebar.

### Booking a Session

- To book a session on the calendar page, you should click on the date you want to book a session for. On clicking the date, the calendar switches to the view where you can select the time slot(s) you want to book.

- In the time slot view, you can see the unavailable time slots for that day. They are highlighted in red. you can only book a session for a time slot that is available. You can also see the time slots that are already booked by you.

- The time slots are in durations of 5 minutes.

- To select a time slot on mobile, long press on the time slot for about 2 seconds until the time slot is highlighted blue. On PC, left click on the time slot. You can then drag the time slot to the duration you want. The time period is displayed on the blue box that appears.

- After selecting an available time slot, a modal appears where you can enter the session title and confirm that the details of the booking are correct. If they are not, you can tap outside the modal and it will close for you reselect the timeslot again.

- After confirming the details, proceed to click on the "Book session" button to book the session. You are required to accept the terms of service which will be displayed on clicking the button. Accept the terms to complete your booking.

- A success notification is displayed on successful booking of the meeting. Else, a notification is displayed with the a reason why the booking failed.

#### Constraints on Booking

The following things have to be noted when booking a session:

- You can only book a session for a day and time that is in the future. You cannot book a session for a past date or time.
Say today is 24th May, 2023. You cannot book a session for 23rd May, 2023 or any time before the current time on 24th May, 2023.

- You can only book a session for a time slot that is available. You cannot book a session for a time slot that is already booked by another user.

- For now, bookings can be made all-week round. There are no restrictions on the days you can book a session.

- The time slots are in durations of 5 minutes, so you can book a session for a minimum of 5 minutes. There is no current maximum duration for a session.

- All booking made are done in the user's timezone. The time displayed on the calendar is also in the user's timezone.
To change your timezone, you can navigate to the settings page and update your timezone.

- Once a session has been booked, you cannot delete it. You can only edit or reschedule the session.

#### Identifying Booked Sessions by Color

The sessions displayed as events on the calendar are color-coded to help you identify them easily. below are the colors and what they represent:

- Light green with white outline - session is pending but does not have a link added yet
- Light green with dark outline - session is pending and has a link added
- Red with white outline - session is cancelled but does not have a link added yet
- Red with dark outline - session is cancelled and has a link added
- Gray - session was missed. That is, the time for the session has passed and the user did not join the meeting, although the link was available.
- Dark green - session has been held. The user joined the meeting at the scheduled time and the admin marked the session as held.

> An event with a dark outline means that the session has a meeting link added to it. You can join the meeting by clicking on the event.

### Editing or Rescheduling a Session

Navigate to the date you booked the session and scroll till you find the session. Click/tap and hold on the session for about 2 seconds until the session is highlighted/lifted. You can then drag the session to the new time slot(s) you want, or change the duration by resizing the event. To exit the edit mode, click on the "Exit edit mode" button that appears at the top of the calendar.

#### Constraints on Editing a Session

The following things have to be noted when editing a session:

- Once a session is in the past, you can only reschedule it to a time greater than the current time. You cannot reschedule a session to a past time. This is to prevent users from rescheduling a session to a time that has already passed.

- The same constraints on booking a session apply to editing a session. You can only edit a session for a day and time that is in the future. You cannot edit a session for a past date or time.

- You do not need to accept the terms of service again when editing a session. You have already done that prior to completing the booking.

### Joining a Meeting

When the time comes for the meeting, you can join the meeting by clicking on the "Join meeting" button on the session card on the dashboard. The link will become active 5mins before the meeting time and will be active for 5mins after the meeting time. The link will be disabled after this time.Also, the link only works if everything is okay with the booking.

### The Settings Page

You can view and edit your profile information on the settings page and also change your password on this page.
There are two forms displayed on the settings page. The first form is for updating your profile information. The second is for changing your password.

### Logging Out

You can log out by clicking on the logout icon at the bottom of the sidebar. This will log you out and redirect you to the login page.

### Forgot Password

Forgot your password? You can reset your password by navigating to the forgot password page from the sign up page. The link to the forgot password page is at the bottom of the sign up form.

Enter your email and click on the "Request reset" button. A password reset link will be sent to your email. Click on the link to reset your password. The link expires after 24 hours.

After clicking on the link, you will be redirected to the password reset page where you can enter your new password and confirm it. Click on the "Reset password" button to reset your password. Note that you will be logged out after resetting your password. Hence, you will need to log in again.

### The Admin Dashboard

The admin dashboard is the default Django admin with some modifications. The admin side panel is divided into 6 sections, each section have models under them. The sections (with their subsections are):

- Users
  - User accounts

- Tokens
  - Password Reset Tokens

- News
  - News

- Links
  - Links

- Booking
  - Sessions
  - Unavailable Periods

- Administration
  - log entries

> NOTE: The datetime shown in the admin dashboard are all in the admin user's timezone. So this means that the time showing for a session that was booked by a user in a different timezone will be displayed in the admin user's timezone. For example, if a user in timezone UTC+3 books a session for 12:00 PM, the admin in timezone UTC+1 will see the session as 10:00 AM.

#### Users

Under the users section, the admin can view all the user accounts in the system. The admin can view the user's email, first name, last name, timezone, and the date the user signed up. The admin can also view the user's last login date and time, and can also create and update user accounts.

Admins can also grant or revoke privileges to a user and also delete a user account.

#### Tokens

Tokens, specifically password reset tokens, are stored here. The admin can view all the password reset tokens that have been generated in the system. The admin can view the user the token was generated for, the token itself, the date the token was generated, and the date the token expires. However, the admin cannot create or update a token. The token can however be deleted. Deleting a token is useful in the advent that a user is having issues with the password reset link sent to them. The admin can delete the token and the user can request for a new password reset link.

#### News

Here, an admin can view all previous added news and updates. To add a new news update, the admin can click on the "Add news" button at the top-right corner of the news page. The admin can then enter the news headline and the news content. The admin can also set the date and time the news should be displayed to the users.

The admin can also update or delete a news update.

#### Links

This section is not to be tampered with, unless when necessary. The links here are like wrappers that contain the meeting links to added to the booked sessions. The links are generated automatically when an admin aprroves a session an adds a meeting link to it.

When the links are deleted, the meeting links are also deleted. The links here have identifiers or code that can be used to form a custom link to the meeting. To visit a link, the admin can just visit the `/booking/links/<link_identifier>` URL.

Don't worry when you update the link in the session the link in the links section will also be updated automatically.

> This means that a user may have just one with (of form `/booking/links/<link_identifier>`) to join the meeting, but if the admin decides to update the link, the user can still use the same link to join the meeting. Also all necessary validations are done before the user is allowed or disallowed to join the meeting.

#### Booking

There are two subsections under the booking section. They are:

- Sessions: This is where the admin can view all the sessions that have been booked by the users. The admin can view the session title, the user that booked the session, the date and time the session was booked, the date and time the session is scheduled for, and the status of the session. The admin can also update the session and delete the session but cannot create a session.

> Admins can only create sessions from the admin panel when the project is still in development mode. In production,  sessions can only be created via the website.

To cancel a session, the admin can update the session and check the "Cancel session" checkbox. The session will be marked as cancelled which will be indicated on the user's calendar on the website.

To add a meeting link to a session, the admin can update the session and enter the meeting link in the "Meeting link" field.

- Unavailable Periods: This is where the admin can add, view and update periods where sessions cannot be booked. There are a few constraints to adding an unavailable period. They are:

  - The date cannot be in the past. You cannot add an unavailable period for a past date.
  - The start and end time of the period cannot also be in the past.
  - You cannot add an unavailable period that overlaps with another unavailable period.
  - You cannot add an unavailable period that overlaps with a booked session. The period since the user already booked before the period was added. So ensure to add unavailable periods prior to users booking sessions, probably days before.

  The admin can also delete an unavailable period.

#### Administration

Only the admin panel logs are stored here. The admin can view logs of all actions that were performed in the admin panel. The admin can view the action that was performed, the user that performed the action, the date and time the action was performed, and the object the action was performed on.

**Logs cannot be updated or deleted.**
