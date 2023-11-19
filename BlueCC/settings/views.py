from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class ChangePassword(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, template_name='settings/password_change.html')

    def post(self, request):
        old_password = request.POST['old_password']
        new_password = request.POST['new_password'].strip()
        new_password_confirm = request.POST['new_password_confirm'].strip()

        if new_password == new_password_confirm:
            if not request.user.has_usable_password() or request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                message_status = True
                message = 'Thay đổi mật khẩu thành công!' if request.user.has_usable_password() else 'Đặt mật khẩu thành công!'
            else:
                message_status = False
                message = 'Mật khẩu không hợp lệ!'
        else:
            message_status = False
            message = 'Mật khẩu không khớp!'

        return render(request=request, template_name='settings/password_change.html', context={
            'message': message,
            'message_status': message_status,
        })


class JobSettings(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, template_name='settings/job_settings.html')

    def post(self, request):
        pass


class ProfileSettings(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, template_name='settings/profile_settings.html')

    def post(self, request):
        pass
