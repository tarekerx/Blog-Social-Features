from django.contrib.auth.models import User, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post


@receiver(post_save,sender = User)
def add_post_permissons(sender,instance,created,**kwargs):
    if created:
        perm = Permission.objects.get(codename = "delete_post")
        instance.user_permissions.add(perm)