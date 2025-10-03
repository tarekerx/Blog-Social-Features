from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse,reverse_lazy
from .models import Post, User, Comment,friend_request
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView
from django import forms
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import AccessMixin
# Home page - view all posts
def index(req):
    posts = Post.objects.all()
    paginator = Paginator(posts,3)
    
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(req, "index.html", {"page_obj": page_obj})


class PostList(LoginRequiredMixin,ListView):
    model = Post
    template_name = "index.html"
    paginate_by = 3
    login_url = "/login/"
    

class PostLikedList(LoginRequiredMixin, ListView):
    model = Post
    template_name = "index.html"
    paginate_by = 3
    login_url = "/login/"   # make sure this route exists
    redirect_field_name = "next"
    def get_queryset(self):
        print("User:", self.request.user)
        print("Authenticated:", self.request.user.is_authenticated)
        return self.request.user.liked_posts.all()






class PostPeopleList(LoginRequiredMixin,ListView):
    model = Post
    template_name = "index.html"
    paginate_by =3
    login_url = "/login/"
    def get_queryset(self):
        user_id = self.kwargs["id"]
        return Post.objects.filter(author =user_id).all()
        

class PostFavouritesList(LoginRequiredMixin,ListView):
    model = Post
    login_url = "/login/"
    paginate_by =3
    template_name = "index.html"
    def get_queryset(self):
        
        return self.request.user.favourite_posts.all()


class PostDetail(LoginRequiredMixin,DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"
    slug_url_kwarg = "id"
    slug_field = "id"
    login_url = "/login/"
    def get_queryset(self):
        return (Post.objects
                .filter()
                .select_related("author"))
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        qs = self.get_queryset()

        context["prev_post"] = qs.filter(id__lt = post.id).order_by("-id").first()
        context["next_post"] = qs.filter(id__gt = post.id).order_by("id").first()
        return context



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title","content"]


class PostCreate(LoginRequiredMixin,CreateView):
    model = Post
    form_class = PostForm
    template_name = "add_post.html"
    login_url = "/login/"

    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("view_post",kwargs = {"id":self.object.id})


class PostUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ["title","content"]
    success_url = reverse_lazy("post")
    login_url = "/login/"
    pk_url_kwarg ="id"
    template_name = "edit_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

    def test_func(self):
        return self.request.user == self.get_object().author
    
    def get_success_url(self):
        return reverse_lazy("view_post",kwargs = {"id":self.object.id})


class PostDelete(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    context_object_name = "post"
    success_url = reverse_lazy("index")

    login_url = "/login/"
    pk_url_kwarg = "id"
    template_name = "post_confirm_delete.html"

    def test_func(self):
        return self.request.user == self.get_object().author



class FriendsRequestsList(LoginRequiredMixin,ListView):
    model = friend_request
    template_name = "friend_requests.html"
    paginate_by = 10
    context_object_name ="friend_requests"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return friend_request.objects.filter(receiver = self.request.user)
    
    
class UserLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = "True"

    def form_invalid(self, form):
        messages.error(self.request,"Wrong email or password")

        return super().form_invalid(form)
    
class UserCreationForm(UserCreationForm):
    class Meta:
        model =User
        fields = ("username","email","password1","password2")
        
class UserRegisterView(AccessMixin,CreateView):
    form_class = UserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("index")


    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # auto-login
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(self.request,"Cannot register while logined")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        # Loop through field errors
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":  # non-field errors
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin,DetailView):
    model = User 
    template_name = "view_profile.html"
    context_object_name = "profile_user"
    pk_url_kwarg = "id"
    login_url = reverse_lazy("login")

class FriendsListView(LoginRequiredMixin,ListView):
    model = User
    template_name = "people.html"
    context_object_name = "users"
    def get_queryset(self):
        return self.request.user.friends.all()
    
    login_url = reverse_lazy("login")
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model= User
        fields = ["username","email","phone_number","bio","avatar"]

class ProfileUpdatView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")
    context_object_name = "user"
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request,"profile updated sucessfuly")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"there is an error while updating the profile")
        response = super().form_invalid(form) 
        return response
    

# Add a new post
@login_required(login_url='login')
def add_post(req):
    if req.method == "POST":
        title = req.POST.get("title")
        content = req.POST.get("content")

        if title and content:
            post = Post(title=title, content=content, author=req.user)
            post.save()
            messages.success(req, "Post added successfully.")
            return redirect(reverse("index"))
        else:
            messages.error(req, "Title and content are required.")

    return render(req, "add_post.html")


# Delete a post (only owner)
@login_required(login_url='login')
def delete_post(req, id):
    post = get_object_or_404(Post, id=id, author=req.user)
    post.delete()
    messages.success(req, "Post deleted successfully.")
    return redirect(reverse("index"))


# Edit a post (only owner)
@login_required(login_url='login')
def edit_post(req, id):
    post = get_object_or_404(Post, id=id, author=req.user)

    if req.method == "POST":
        title = req.POST.get("title")
        content = req.POST.get("content")

        if title and content:
            post.title = title
            post.content = content
            post.save()
            messages.success(req, "Post updated successfully.")
            return redirect(reverse("index"))
        else:
            messages.error(req, "Title and content are required.")

    return render(req, "edit_post.html", {"post": post})


# View a single post
@login_required(login_url='login')
def view_post(req, id):
    post = get_object_or_404(Post, id=id)
    return render(req, "post.html", {"post": post})


# Register view
def register_view(req):
    if req.method == "POST":
        username = req.POST.get("username")
        email = req.POST.get("email")
        password1 = req.POST.get("password1")
        password2 = req.POST.get("password2")
        phone_number = req.POST.get("phone_number") or None

        # Validation
        if not username or not email or not password1:
            messages.error(req, "All fields are required.")
            return render(req, "register.html")

        if password1 != password2:
            messages.error(req, "Passwords do not match.")
            return render(req, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(req, "Username already exists.")
            return render(req, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(req, "Email already exists.")
            return render(req, "register.html")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            phone_number=phone_number
        )
        user.save()

        messages.success(req, "Registration successful. Please log in.")
        return redirect(reverse("login"))

    return render(req, "register.html")


# Login view
def login_view(req):
    if req.user.is_authenticated:
        messages.info(req, "You are already logged in.")
        return redirect(reverse("index"))

    if req.method == "POST":
        email = req.POST.get("email")
        password = req.POST.get("password1")

        if not email or not password:
            messages.error(req, "Email and password are required.")
            return render(req, "login.html")

        # ⚠️ WARNING: Django's default auth uses username, not email
        # You must have a custom backend or use email as username
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(req, "Invalid email or password.")
            return render(req, "login.html")

        user = authenticate(req, email=email, password=password)

        if user is not None:
            login(req, user)
            messages.success(req, "Login successful.")
            return redirect(reverse("index"))
        else:
            messages.error(req, "Invalid email or password.")

    return render(req, "login.html")


# User profile (edit info)
@login_required(login_url='login')
def profile(req):
    if req.method == "POST":
        username = req.POST.get("username")
        email = req.POST.get("email")
        password1 = req.POST.get("password1")
        password2 = req.POST.get("password2")
        first_name = req.POST.get("first_name")
        last_name = req.POST.get("last_name")
        bio = req.POST.get("bio")
        phone_number = req.POST.get("phone_number")

        # Update fields only if changed
        if username and username != req.user.username:
            if User.objects.filter(username=username).exists():
                messages.error(req, "Username already taken.")
                return render(req, "profile.html")
            req.user.username = username

        if email and email != req.user.email:
            if User.objects.filter(email=email).exists():
                messages.error(req, "Email already in use.")
                return render(req, "profile.html")
            req.user.email = email

        if first_name is not None:
            req.user.first_name = first_name
        if last_name is not None:
            req.user.last_name = last_name
        if bio is not None:
            req.user.bio = bio
        if phone_number is not None:
            req.user.phone_number = phone_number

        # Handle password
        if password1 and password2:
            if password1 != password2:
                messages.error(req, "Passwords do not match.")
                return render(req, "profile.html")
            req.user.set_password(password1)
            update_session_auth_hash(req, req.user)  # Keep user logged in

        req.user.save()
        messages.success(req, "Profile updated successfully.")

    return render(req, "profile.html")


# Logout view
@login_required(login_url='login')
def logout_view(req):
    logout(req)
    messages.success(req, "Logged out successfully.")
    return redirect(reverse("index"))


# Like/unlike a post
@login_required(login_url='login')
def like_post(req, post_id):
    post = get_object_or_404(Post, id=post_id)

    if req.user in post.likes.all():
        post.likes.remove(req.user)
    else:
        post.likes.add(req.user)

    return redirect(reverse("view_post", kwargs={"id": post.id}))


# Add comment to post
@login_required(login_url='login')
def comment_on_post(req, id):
    post = get_object_or_404(Post, id=id)
    content = req.POST.get("comment")

    if not content:
        messages.error(req, "Comment cannot be empty.")
        return redirect(reverse("view_post", kwargs={"id": post.id}))

    comment = Comment(post=post, author=req.user, content=content)
    comment.save()
    messages.success(req, "Comment added.")
    return redirect(reverse("view_post", kwargs={"id": post.id}))


# Edit comment (only owner)
@login_required(login_url='login')
def edit_comment(req, id):
    comment = get_object_or_404(Comment, id=id, author=req.user)
    post_id = comment.post.id

    if req.method == "POST":
        content = req.POST.get("comment")
        if content:
            comment.content = content
            comment.save()
            messages.success(req, "Comment updated.")
            return redirect(reverse("view_post", kwargs={"id": post_id}))
        else:
            messages.error(req, "Comment content is required.")

    return render(req, "post.html", {
        "post": comment.post,
        "edit_comment": comment
    })


# Delete comment (only owner)
@login_required(login_url='login')
def delete_comment(req, id):
    comment = get_object_or_404(Comment, id=id, author=req.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(req, "Comment deleted.")
    return redirect(reverse("view_post", kwargs={"id": post_id}))


# Request admin status via email
@login_required(login_url='login')
def ask_for_admin(req):
    if req.method == "POST":
        message = req.POST.get("message")
        email = req.user.email

        if not message:
            messages.error(req, "Message is required.")
            return render(req, "ask_for_admin.html")

        full_message = f"User {email} wants to become an admin.\nReason: {message}"

        try:
            sent = send_mail(
                subject="Admin Access Request",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["tarekihape@gmail.com"],
                fail_silently=False,
            )
            if sent:
                messages.success(req, "Your request has been sent.")
            else:
                messages.error(req, "Failed to send request.")
        except Exception as e:
            messages.error(req, f"Error sending email: {e}")

        return redirect(reverse("index"))

    return render(req, "ask_for_admin.html")


@login_required(login_url='login')
def liked_posts(req):

    posts = req.user.liked_posts.all()
    paginator = Paginator(posts,3)
    
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(req, "index.html", {"page_obj": page_obj})


@login_required(login_url='login')
def favourite_posts(req):

    posts = req.user.favourite_posts.all()
    paginator = Paginator(posts,3)
    
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(req, "index.html", {"page_obj": page_obj})


    return render(req,"index.html",{"posts":posts})


@login_required(login_url='login')
def add_post_to_favourites(req,id):

    post = get_object_or_404(Post,id=id)
    if req.user in post.favourites.all():
        post.favourites.remove(req.user)
    else:
        post.favourites.add(req.user)

    return redirect(reverse("view_post",kwargs={"id":id}))


@login_required(login_url='login')
def show_people(req):
    users = User.objects.all()
    return render(req,"people.html",{"users":users})


@login_required(login_url='login')
def show_profile(req,id):
    user = get_object_or_404(User,id=id)
    is_friend = req.user.friends.filter(id=user.id).exists()
    return render(req,"view_profile.html",{"profile_user":user,"is_friend":is_friend})


@login_required(login_url='login')
def people_posts(req,id):
    user = get_object_or_404(User,id=id)
    posts = user.posts.all()

    paginator = Paginator(posts,3)
    
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(req,"index.html",{"page_obj":page_obj})


@login_required(login_url='login')
def send_friend_request(req,id):
    receiver = get_object_or_404(User,id=id)
    
    if not friend_request.objects.filter(sender=req.user,receiver=receiver).exists() and not req.user.friends.filter(id=receiver.id).exists():
        friend_request.objects.create(sender=req.user,receiver=receiver)
        messages.success(req, "Friend request sent.")
        return redirect(reverse("show_profile",kwargs={"id":receiver.id}))

    messages.error(req,"can not friend request send to existed friend ")
    return redirect(reverse("show_profile",kwargs={"id":receiver.id}))


@login_required(login_url='login')
def friend_requests(req):
    friend_requests = friend_request.objects.filter(receiver=req.user)
    return render(req,"friend_requests.html",{"friend_requests":friend_requests})


@login_required(login_url='login')
def accept_friend_request(req,id):
    fr = get_object_or_404(friend_request,id=id ,receiver=req.user)

    req.user.friends.add(fr.sender)
    req.user.save()
    fr.delete()

    messages.success(req, "Friend request accepted.")
    return redirect(reverse("friend_requests"))


@login_required(login_url='login')
def decline_friend_request(req,id):
    fr = get_object_or_404(friend_request,id=id ,receiver=req.user)

    fr.delete()
    messages.success(req, "Friend request rejected.")
    return redirect(reverse("friend_requests"))
    


@login_required(login_url='login')
def friends(req):
    friends = req.user.friends.all()
    return render(req,"people.html",{"users":friends})


@login_required(login_url='login')
def search(req):
    posts = Post.objects.filter(title__contains=req.POST.get("q") if req.POST.get("q") else "")
    
    paginator = Paginator(posts,3)
    
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(req, "index.html", {"page_obj": page_obj})
