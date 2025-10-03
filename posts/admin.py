from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email',)

    fieldsets = (
        (None, {"fields":("email","username", "password")}),
        ("personale info",{"fields":("first_name", "last_name", "bio", "phone_number")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "phone_number", "password1", "password2", "is_staff", "is_active")}
        ),
    )

    search_fields = ('email', 'username',"is_staff", "is_active")
    ordering = ('email',)
    


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'updated_at', 'author')
    ordering = ('-created_at',)