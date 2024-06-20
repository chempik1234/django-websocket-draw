from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .forms import SignInForm, SignUpForm
from .jwt import create_token
from .models import Room, RoomCell


def reset_rooms_cache():
    all_rooms = Room.objects.all().values("pk", "name", "host")
    cache.delete('rooms')
    cache.set('rooms', all_rooms, 60 * 60)  # 1h


def create_room(name, user, width):
    created_room = Room.objects.create(name=name, host=user)
    for number in range(width * width):
        RoomCell.objects.create(room=created_room, number=number, r=255, g=255, b=255)
    return created_room


def index(request):
    rooms = cache.get('rooms')
    if request.method == "POST":
        name = request.POST.get("name", None)
        width_str = request.POST.get("width", None)
        if name is not None and width_str is not None:
            new_room = create_room(name, request.user, int(width_str))
            reset_rooms_cache()
            return HttpResponseRedirect(reverse("drawing:room", kwargs={"pk": new_room.pk}))  # /room/1/
    if rooms is None:
        reset_rooms_cache()
        rooms = cache.get('rooms')
    return render(request, "drawing/index.html", context={"rooms": rooms})


def room(request, pk):
    room_to_join: Room = get_object_or_404(Room, pk=pk)
    return render(request, "drawing/room.html", context={"room": room_to_join,
                                                         "title": f"Drawing room #{room_to_join.pk}"})


class SignInView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'drawing/auth_form.html'

    def get(self, request, form=None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('drawing:index')
        if form is None:
            form = SignInForm()
        data_context = {"title": "Drawing: Sign in", "form": form,
                        "post_url": reverse("drawing:sign_in")}
        return Response(data_context)

    def post(self, request):
        post = SignInForm(request.POST)
        if post.is_valid():
            post.clean()
            username = post.cleaned_data.get('username')
            password = post.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse(create_token(user))
        return JsonResponse({"details": "Invalid form"}, status=HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "drawing/auth_form.html"

    def get(self, request, form=None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('drawing:index')
        if form is None:
            form = SignUpForm()
        data_context = {"title": "Drawing: Sign Up", "form": form,
                        "post_url": reverse("drawing:sign_up")}
        return Response(data_context)

    def post(self, request):
        post = SignUpForm(request.POST)
        if post.is_valid():
            user = post.save()
            login(request, user)
            return JsonResponse(create_token(user))
        else:
            return JsonResponse({"details": "Invalid form"}, status=HTTP_400_BAD_REQUEST)


@login_required(login_url='drawing:sign_in')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class RoomDeleteView(APIView):
    def post(self, request, pk):
        room_to_delete: Room = get_object_or_404(Room, pk=pk)
        if room_to_delete.host == request.user:
            room_to_delete.delete()
            reset_rooms_cache()
            return Response(status=HTTP_200_OK)
        else:
            return Response({"details": "Not your room!"}, status=HTTP_403_FORBIDDEN)
