from django.contrib import admin
from .models import MediaFile, AudioFile,Student,Course,authors,books

# admin.site.register(MediaFile)
# admin.site.register(AudioFile)
# admin.site.register(Student)
# admin.site.register(Course)
admin.site.register(authors)
admin.site.register(books)