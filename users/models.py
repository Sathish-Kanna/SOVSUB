from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from PIL import Image
from PIL import ImageFile


ImageFile.LOAD_TRUNCATED_IMAGES = True


class Candidate(models.Model):
    candidate_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    booth_id = models.CharField(max_length=10)
    otp = models.CharField(max_length=6, blank=True)
    otp_time = models.CharField(max_length=20, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?\d{10,12}$',
                                 message='Phone number must be entered in the format: "+919876543210"')
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    image = models.ImageField(upload_to='candidate_img', blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    voter_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    booth_id = models.CharField(max_length=10)
    registered = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_time = models.CharField(max_length=20, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?\d{10,12}$',
                                 message='Phone number must be entered in the format: "+919876543210"')
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    image = models.ImageField(upload_to='voter_img', blank=True)

    def __str__(self):
        return str(self.__dict__)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        '''img = Image.open(self.image.path)
        print('Profile saved in model')

        if img.height > 250 or img.width > 250:
            output_size = (250, 250)
            img.thumbnail(output_size)
            img.save(self.image.path)'''
