from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q

from direct.forms import DirectForm
from direct.models import Message


@login_required
def direct(request, pk):
    if request.user.id == pk:
        directs = Message.objects.filter(Q(recipient_id=pk) | Q(sender_id=pk))
        form = DirectForm
        context = {
            'directs': directs,
            'form': form,
        }
        return render(request, 'direct.html', context)
    else:
        messages.success(request, "Unavailable link...")
        return redirect('home')


class CreateDirectView(CreateView):
    model = Message
    # form_class = DirectForm
    template_name = "message_form.html"
    fields = ['body']
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return User.objects.get(id=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.get_queryset()
        return super().form_valid(form)


@login_required
def message_read(request, pk):
    message = Message.objects.get(id=pk)
    message.is_read = True
    message.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def message_delete(request, pk):
    messange = Message.objects.get(id=pk)
    messange.delete()
    return redirect(request.META.get('HTTP_REFERER'))


