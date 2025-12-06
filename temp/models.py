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