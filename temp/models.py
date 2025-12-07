from django.db import models

# Create your models here.
# from cloudinary_storage.storage import MediaCloudinaryStorage

# class MediaFile(models.Model):
#     title = models.CharField(max_length=100)
#     file = models.FileField(
#         storage=MediaCloudinaryStorage(),  # forces Cloudinary storage
#         upload_to='images/'  # Cloudinary folder
#     )


# from django.db import models
# from cloudinary_storage.storage import VideoMediaCloudinaryStorage

# class AudioFile(models.Model):
#     title = models.CharField(max_length=100)
#     audio = models.FileField(
#         storage=VideoMediaCloudinaryStorage(),  # for audio files
#         upload_to='ielts_audio/'
#     )

#     def __str__(self):
#         return self.title


class Student(models.Model):
    name = models.CharField(max_length=100)

class Course(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(Student)


class authors(models.Model):
    name = models.CharField(max_length=100)
    qualifion = models.JSONField(null=True, blank=True)
    qualification = models.JSONField(null=True, blank=True, default=dict)

class books(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(authors, on_delete=models.CASCADE)

class a(models.Model):
    book = models.ForeignKey(books, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
class Chapter(models.Model):
    book = models.ForeignKey(books, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
class mcq(models.Model):
    question = models.CharField(max_length=255)
    options = models.JSONField(default=list)  # List of options
    correct_answer = models.CharField(max_length=255)  # Correct option

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    metadata = models.JSONField(blank=True, null=True)  # list/dict data রাখার জন্য
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
