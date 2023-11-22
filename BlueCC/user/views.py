from allauth.account.models import EmailAddress
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from user.models import User
from django.views import View

from user.tokens import account_activation_token
from utils.utils import is_safe_url, send_email
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model


class UserSignin(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, template_name='user/login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        policy_check = request.POST.get('policy_check', None)
        user = authenticate(request, email=email, password=password)

        if user and policy_check in ['policy_check']:
            login(request, user)

            redirect_to = request.POST.get('next', 'home')
            if is_safe_url(url=redirect_to, allowed_hosts=request.get_host()):
                return redirect(redirect_to)
        message = 'Vui lòng đồng ý với chính sách của chúng tôi!' if not policy_check else 'Email hoặc mật khẩu không chính xác!'

        return render(request, template_name='user/login.html', context={
            'message': message
        })


class UserSignout(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class UserRegister(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, template_name='user/signup.html')

    def post(self, request):
        full_name = request.POST['full_name'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()
        password_confirm = request.POST['confirm'].strip()
        policy_check = request.POST.get('policy_check', None)

        message = 'Mật khẩu không khớp!' if not password == password_confirm else \
            'Vui lòng đồng ý với chính sách của chúng tôi!' if policy_check not in ['policy_check'] else None
        message_status = False

        if password == password_confirm and policy_check in ['policy_check']:
            user = User.objects.create_user(full_name=full_name, email=email, password=password)
            emailaddress = EmailAddress.objects.add_email(request, user, user.email)
            emailaddress.send_confirmation(request)

            message = 'Gửi email xác nhận thành công. Vui lòng kiểm tra hòm thư của bạn!'
            message_status = True

        return render(request, template_name='user/signup.html', context={
            'message': message,
            'message_status': message_status,
        })


class UserPasswordReset(View):
    def get(self, request):
        return render(request, template_name='user/password_reset.html')

    def post(self, request):
        email = request.POST['email']
        policy_check = request.POST.get('policy_check', None)

        user = User.objects.filter(email=email).first()

        message = 'Tài khoản không tồn tại!' if not user else \
            'Vui lòng đồng ý với chính sách của chúng tôi!' if policy_check not in ['policy_check'] else None
        message_status = False

        if user and policy_check in ['policy_check']:
            mail_result = send_email(request,
                                     user=user,
                                     to_email=email,
                                     mail_subject='Password reset',
                                     template='user/email/template_password_reset.html',
                                     message_success='Đã gửi yêu cầu thay đổi mật khẩu đến email của bạn!')

            message = mail_result['message']
            message_status = mail_result['message_status']

        return render(request, template_name='user/password_reset.html', context={
            'message': message,
            'message_status': message_status,
        })


class PasswordSet(View):
    def get(self, request, uidb64=None, token=None):
        user = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = user.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, user.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            return render(request, template_name='user/password_set.html', context={
                'uid': uidb64,
                'token': token,
            })
        else:
            message_status = False
            message = 'Đường dẫn không hợp lệ!'

        return render(request, template_name='user/login.html', context={
            'message': message,
            'message_status': message_status,
        })

    def post(self, request, uidb64=None, token=None):
        user = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = user.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, user.DoesNotExist):
            user = None

        message = 'Đường dẫn không hợp lệ!'
        message_status = False

        if user is not None and account_activation_token.check_token(user, token):
            new_password = request.POST['new_password'].strip()
            confirm_new_password = request.POST['confirm_new_password'].strip()
            url = request.build_absolute_uri()

            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                message = 'Thay đổi mật khẩu thành công!'
                message_status = True
            else:
                message = 'Mật khẩu không khớp!'
                return redirect(reverse(url, kwargs={
                    'message': message,
                    'message_status': message_status,
                }))

        return render(request, template_name='user/login.html', context={
            'message': message,
            'message_status': message_status,
        })