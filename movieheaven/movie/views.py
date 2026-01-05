from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView,DetailView, CreateView, DeleteView, UpdateView
from .models import Movie,Comment, MovieFolder, Like
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Count

def home(request):
    return render(request, 'movie/home.html')

class MovieListView(ListView):
    model= Movie
    template_name='movie/film_list.html'
    context_object_name= 'films'
    ordering=['-title']
    paginate_by=10
    
def search(request):
    searched = request.GET.get('searched', '')
    
    if searched:
        films = Movie.objects.filter(title__icontains=searched)
    else:
        films = []
    return render(request, 'movie/film_search.html', {'films': films})

class MovieDetailView(DetailView):
    model=Movie

    def post(self, request, *args, **kwargs):
        movie = self.get_object()  # Get the movie object using the pk passed in the URL
        if request.method == 'POST':
            comment_text = request.POST.get('comment', '')
            if comment_text:
                Comment.objects.create(user=request.user, text=comment_text, movie=movie)
        return redirect('film_detail', pk=movie.pk)

@login_required
def commentdelete(request, pk):
    comment= Comment.objects.get(id=pk)
    if request.user == comment.user:
        comment.delete()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

class FolderCreateView(LoginRequiredMixin,CreateView):
    model = MovieFolder
    fields= ['title','description','image']
    success_url= reverse_lazy('lists')

    def form_valid(self, form):
        form.instance.user= self.request.user
        return super().form_valid(form)

class FolderListview(ListView):
    model= MovieFolder
    context_object_name='folders'

    def get_queryset(self):
        return MovieFolder.objects.annotate(
                total_likes=Count('likes')
            ).order_by('-total_likes')[:3]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = MovieFolder.objects.all().order_by('-created_at')[:3] 

        context['recent'] = queryset
        return context

class FolderDetailView(DetailView):
    model=MovieFolder
    context_object_name='folder'

def folderdelete(request,slug):
    folder= MovieFolder.objects.get(slug=slug)
    if request.user==folder.user:   
        folder.delete()
    return redirect('lists')



def addtolist(request):
    if request.method == "POST":
        movie_id = request.POST.get('movie_id')
        
        if movie_id:  
            # Save movie_id in session for next request
            request.session['movie_id'] = movie_id

        # Get movie_id from session if not in request
        movie_id = request.session.get('movie_id')

        movie = get_object_or_404(Movie, id=movie_id)

        list_id = request.POST.get('movie_folder_id')
        if list_id:
            folder = MovieFolder.objects.get(id=list_id, user=request.user)
            folder.movie.add(movie)
            messages.success(request, f"'{movie.title}' added to '{folder.title}'.")
            return redirect('film_detail', pk=movie.id)

        # If list_id is not in request, show selection page
        lists = MovieFolder.objects.filter(user=request.user)
        if not lists:
            messages.error(request, "You have no lists available.")
            return render(request, 'movie/user_list.html', {'lists': None, 'movie': movie})

        return render(request, 'movie/user_list.html', {'lists': lists, 'movie': movie})
    

def likes(request,pk):
    folder= MovieFolder.objects.get(id=pk)
    like, created = Like.objects.get_or_create(user=request.user, folder=folder)

    if  not created:  
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

class PopularList(ListView):
    model= MovieFolder
    template_name='moviefolder_list.html'

    #def get_queryset(self):
    #    return MovieFolder.objects.filter()



class MovieCreateView(UserPassesTestMixin,CreateView):
    model= Movie
    fields='__all__'
    success_url= reverse_lazy('film_list')
    template_name= 'movie/movie_create.html'

    def test_func(self):
        return self.request.user.is_superuser  #returns true giving permission to superuseronly

    def handle_no_permission(self): 
        return redirect('home')
    
    '''or can do this instead of handle_no_permission:
     raise_exception = True '''

class MovieUpdateView(UserPassesTestMixin, UpdateView):
    model=Movie
    fields='__all__'
    template_name= 'movie/movie_edit.html'


    def test_func(self):
        return self.request.user.is_superuser  #returns true giving permission to superuseronly

    def handle_no_permission(self): 
        return redirect('home')
    




    

            
        
    
    

        














    

    