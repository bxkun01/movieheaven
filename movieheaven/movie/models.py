from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Movie(models.Model):
    title= models.CharField(max_length=200)
    description= models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='movie_posters/')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('film_detail', kwargs={'pk':self.pk})
    
class Comment(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,related_name="comments", on_delete=models.CASCADE) 
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.movie.title}"

class MovieFolder(models.Model):
    user= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='folders')
    movie= models.ManyToManyField(Movie, related_name='folders',blank=True )
    title= models.CharField(max_length=80)
    description= models.TextField(blank=True, null=True)
    image= models.ImageField(default='default_folder.png',upload_to='folder_image')
    created_at= models.DateField(auto_now_add=True)
    slug= models.SlugField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug=slugify(self.title)
        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"'{self.title}' list by {self.user if self.user else 'Unknown'}"
    
    @property
    def like_count(self):
        return self.likes.count() 



class  Like(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    folder=models.ForeignKey(MovieFolder, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'folder') 



    
    