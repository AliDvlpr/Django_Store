from django.shortcuts import render


def say_that(request):
    return render(request, 'hello.html', {'name': 'AliDVLPR'})
