from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    following = models.ManyToManyField(User, related_name="folowers", blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'


"""
These functions ensure that a UserProfile is automatically created 
for every new user, which is crucial for the follow system to work. 
"""    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()