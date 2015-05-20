from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext

from .forms import BookingForm, ViewBookingsForm, CancelBookingForm
from .models import Booking, Feedback
from django.core.mail import EmailMessage
from datetime import timedelta
import datetime


"""
This view is used for logging in the user. It will be show login page if the user is not logged in, otherwise it 
will redirect the user to the home page.
"""
def login_view(request):
	state = "Please log in below..."
	username = password = ''
	if request.POST:
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')
		else:
			state = "Your username and/or password were incorrect."
	else:
		state = ""
	return render_to_response('registration/login.html', locals(), context_instance=RequestContext(request))


"""
The Logout button calls this view and it will return back to the default login page.
"""
def logout_view(request):
	from django.contrib.auth.views import logout
	logout(request)
	return HttpResponseRedirect(reverse("home.views.home"))
	# return render(request, "registration/logout.html")


"""
This will open the home page if the user is already loggedin otherwise it will rediect to the login page.
"""
@login_required
def home(request):
	return render(request, "home/home.html", {})


"""
View for 'click to book' page. If there is no errors in the form then it will be saved and a thanks page will be 
displayed and a email alert will be send to the admin as well as the user's emailID.
"""
@login_required
def book(request):
	if request.method == 'POST':
		form = BookingForm(request.POST)
		name = request.POST['name']
		email = request.user.email
		print email	

		if form.is_valid():
			value = form.save(commit=False)
			user = User.objects.all()
			value.email = request.user.email
			value.save()
			# user_email = EmailMessage('Booking System', 'Hi ' + name + ', Thanks for booking :)', to=[email])
			# user_email.send()
			return render(request, "home/thanks.html", {})
	else:
		form = BookingForm()
	return render(request, "home/book.html", {"form": form})
	# alternative of context, locals()


""" 
This view is linked with the "View bookings" page and it will return only those bookings whose status is true set
(finalized) by the admin.
"""
@login_required
def view(request):
	if request.method == 'POST':
		form = ViewBookingsForm(request.POST)
		view_hall = request.POST['hall']
		view_date = request.POST['date']
		if form.is_valid():
			boo = Booking.objects.filter(status = 1, hall = view_hall, date = view_date)
			return render(request, "home/view_booking.html", {"booking": boo})
	else:
		form = ViewBookingsForm()
	return render(request, "home/view.html", {"form": form})


"""
This view will list the booking made by loggedin user such that the user can send a cancellation request to admin for 
the event selected by user.
"""
@login_required
def cancel(request):
	email = request.user.email
	can = Booking.objects.filter(status=1, email=email, date__gt = datetime.date.today())
	return render(request, "home/cancel.html", {'cancel': can})


"""
Used for cancelling the event using radio button and the user will cancel the event
"""
@login_required
def cancelbooking(request):
	cancel_state = "Event cancelled"
	event = ''
	if request.POST:
		event = request.POST.get('cancel')
		cancel = Booking.objects.filter(event_name = event).delete()
		# can = Booking.objects.filter(status=1, email=email, date__gt = datetime.date.today())
		return HttpResponseRedirect('/cancel/')
	else:
		cancel_state = "Event not cancelled"
		can = Booking.objects.filter(status=1, email=email, date__gt = datetime.date.today())
	return render_to_response('home/cancel.html', locals(), context_instance=RequestContext(request))


"""
This function is used to store the feedback from any user to the database.
"""
def feedback(request):
	feed_state = "Feedback given"
	feed_name = feed_email = feed_contact = feed_note = ""
	if request.POST:
		feed_name = request.POST.get('name')
		feed_email = request.POST.get('email')
		feed_contact = request.POST.get('mob')
		feed_note = request.POST.get('feed')
		
		review = Feedback(name = feed_name, email = feed_email, contact = feed_contact, feedback = feed_note)
		review.save()
		return render(request, "home/feedback.html", {})
	else:
		feed_state = "Please enter valid details"
	return render_to_response('registration/login.html', locals(), context_instance=RequestContext(request))
