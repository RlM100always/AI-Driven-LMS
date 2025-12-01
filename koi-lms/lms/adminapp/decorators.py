from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in as a teacher.')
            return redirect('admin_login')
        
        try:
            teacher = request.user.teacher_profile
            if not teacher.is_active:
                messages.error(request, 'Your account is inactive.')
                return redirect('admin_login')
        except:
            messages.error(request, 'You do not have teacher access.')
            return redirect('admin_login')
        
        return view_func(request, *args, **kwargs)
    return wrapper