from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from chat.forms import ChatForm
from chat.models import Chat


@login_required
def chat(request):
    if request.method == 'POST':
        form = ChatForm(request.POST or None)
        form.instance.sender = request.user
        if form.is_valid():
            form.save()
            return redirect('chat')
    else:
        chats = Chat.objects.all()
        form = ChatForm()
        context = {
            'chats': chats,
            'title': 'Chat',
            'form': form,
        }
        return render(request, 'chat.html', context)


