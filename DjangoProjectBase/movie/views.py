from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.management.base import BaseCommand
from movie.models import Movie
import os
import numpy as np
from dotenv import load_dotenv, find_dotenv
import json
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity


import openai
from openai.embeddings_utils import get_embedding, cosine_similarity

from dotenv import load_dotenv, find_dotenv

from .models import Movie, Review

from .forms import ReviewForm

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm: 
       movies = Movie.objects.filter(title__icontains=searchTerm) 
    else: 
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': movies})


def about(request):
    return render(request, 'about.html')


def detail(request, movie_id):
    movie = get_object_or_404(Movie,pk=movie_id)
    reviews = Review.objects.filter(movie = movie)
    return render(request, 'detail.html',{'movie':movie, 'reviews': reviews})

def recommendations(request):
    searchTerm = request.GET.get('recommendations')
    movie = Movie.objects.all()
    if (searchTerm):
        _ = load_dotenv('../openAI.env')
        openai.api_key  = os.environ['openAI_api_key']

        with open('../movie_descriptions_embeddings.json', 'r') as file:
            file_content = file.read()
            movies = json.loads(file_content)


        emb = get_embedding(movies[1]['description'],engine='text-embedding-ada-002')
        print(movies[27]['title'])
        print(movies[3]['title'])
        print(movies[20]['title'])

        print(f"Similitud entre película {movies[27]['title']} y {movies[3]['title']}: {cosine_similarity(movies[27]['embedding'],movies[3]['embedding'])}")
        print(f"Similitud entre película {movies[27]['title']} y {movies[20]['title']}: {cosine_similarity(movies[27]['embedding'],movies[20]['embedding'])}")
        print(f"Similitud entre película {movies[20]['title']} y {movies[3]['title']}: {cosine_similarity(movies[20]['embedding'],movies[3]['embedding'])}")

        req = searchTerm
        emb = get_embedding(req,engine='text-embedding-ada-002')

        sim = []
        for i in range(len(movies)):
            sim.append(cosine_similarity(emb,movies[i]['embedding']))
        sim = np.array(sim)
        idx = np.argmax(sim)
        recommendation = (movies[idx]['title'])
        movie = Movie.objects.filter(title=recommendation) 
        print(movie)

    return render(request,"recommendations.html", {'movies':movie})


@login_required
def createreview(request, movie_id):
    movie = get_object_or_404(Movie,pk=movie_id)
    if request.method == 'GET':
        return render(request, 'createreview.html',{'form':ReviewForm(), 'movie': movie})
    else:
        try:
            form = ReviewForm(request.POST)
            newReview = form.save(commit=False)
            newReview.user = request.user
            newReview.movie = movie
            newReview.save()
            return redirect('detail', newReview.movie.id)
        except ValueError:
            return render(request, 'createreview.html',{'form':ReviewForm(),'error':'bad data passed in'})

@login_required       
def updatereview(request, review_id):
    review = get_object_or_404(Review,pk=review_id,user=request.user)
    if request.method =='GET':
        form = ReviewForm(instance=review)
        return render(request, 'updatereview.html',{'review': review,'form':form})
    else:
        try:
            form = ReviewForm(request.POST, instance=review)
            form.save()
            return redirect('detail', review.movie.id)
        except ValueError:
            return render(request, 'updatereview.html',{'review': review,'form':form,'error':'Bad data in form'})
        
@login_required
def deletereview(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    review.delete()
    return redirect('detail', review.movie.id)