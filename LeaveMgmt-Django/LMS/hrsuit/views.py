from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest


def index_view(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html", {})
