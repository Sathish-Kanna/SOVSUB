from django.contrib import admin
from .models import Profile
from .models import Candidate

admin.site.register(Profile)
admin.site.register(Candidate)