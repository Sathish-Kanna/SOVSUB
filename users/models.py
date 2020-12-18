from django.db import models
from django.core.validators import RegexValidator

from PIL import Image
from PIL import ImageFile


ImageFile.LOAD_TRUNCATED_IMAGES = True


class Profile(models.Model):
    voter_id = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100, blank=True)
    booth_id = models.TextField(max_length=10, blank=True)
    registered = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_time = models.CharField()
    phone_regex = RegexValidator(regex=r'^\+?\d{10,12}$',
                                 message='Phone number must be entered in the format: "+919876543210"')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    image = models.ImageField(upload_to='voter_img')

    def __str__(self):
        return str(self.name)+' Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        print('Profile saved in model')

        if img.height > 250 or img.width > 250:
            output_size = (250, 250)
            img.thumbnail(output_size)
            img.save(self.image.path)
