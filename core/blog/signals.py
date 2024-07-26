from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver, Signal
from django.shortcuts import get_object_or_404, render

from .models import Post

post_viewed = Signal(providing_args=["instance", "user"])


@receiver(pre_save, sender=Post)
def before_post_save(sender, instance, **kwargs):
    print(f"About to save post: {instance.title}")


@receiver(post_save, sender=Post)
def after_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"Post created: {instance.title}")
    else:
        print(f"Post updated: {instance.title}")


@receiver(post_delete, sender=Post)
def after_post_delete(sender, instance, **kwargs):
    print(f"Post deleted: {instance.title}")


@receiver(m2m_changed, sender=Post.tags.through)
def post_tags_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        print(f"Post added: {instance.title}")
    elif action == "post_remove":
        print(f"Post removed: {instance.title}")


# ОТправить сигнал
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_viewed.send(sender=Post, instance=post, user=request.user)
    return render(request, "blog/detail.html")
