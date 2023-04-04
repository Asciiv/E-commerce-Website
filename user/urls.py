from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from user.views import login_view, resend_otp, signup,islogin

urlpatterns = [
	path('signup/', signup, name = 'signup'),
	path('login/', login_view, name = 'login'),
	# path('login/', LoginView.as_view(template_name = 'user/login.html', redirect_authenticated_user = True), 
 #    	name = 'login'),
	path('logout/', LogoutView.as_view(next_page = 'login'), name = 'logout'),

	path("password-reset/", 
    	PasswordResetView.as_view(template_name='shop/password_reset.html'),
    	name="password_reset"),

	path("password-reset/done/", 
		PasswordResetDoneView.as_view(template_name='shop/password_reset_done.html'), 
		name="password_reset_done"),

	path("password-reset-confirm/<uidb64>/<token>/", 
		PasswordResetConfirmView.as_view(template_name='shop/password_reset_confirm.html'), 
		name="password_reset_confirm"),

	path("password-reset-complete/", 
		PasswordResetCompleteView.as_view(template_name='shop/password_reset_complete.html'), 
		name="password_reset_complete"),
    path('resendOTP', resend_otp),
    path('islogin', islogin),

]