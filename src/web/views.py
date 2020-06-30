from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.http import Http404
from .models import Movie,Myrating
from django.contrib import messages
from .forms import UserForm
from django.db.models import Case, When
from .recommendation import Myrecommend
import numpy as np 
import pandas as pd
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes,permission_classes,api_view
# for recommendation
def recommend(request):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	df=pd.DataFrame(list(Myrating.objects.all().values()))
	nu=df.user_id.unique().shape[0]
	current_user_id= request.user.id
	# if new user not rated any movie
	if current_user_id>nu:
		movie=Movie.objects.get(id=15)
		q=Myrating(user=request.user,movie=movie,rating=0)
		q.save()

	print("Current user id: ",current_user_id)
	prediction_matrix,Ymean = Myrecommend()
	my_predictions = prediction_matrix[:,current_user_id-1]+Ymean.flatten()
	pred_idxs_sorted = np.argsort(my_predictions)
	pred_idxs_sorted[:] = pred_idxs_sorted[::-1]
	pred_idxs_sorted=pred_idxs_sorted+1
	print(pred_idxs_sorted)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pred_idxs_sorted)])
	movie_list=list(Movie.objects.filter(id__in = pred_idxs_sorted,).order_by(preserved)[:10])
	return render(request,'web/recommend.html',{'movie_list':movie_list})


# List view
def index(request):
	movies = Movie.objects.all()
	query  = request.GET.get('q')
	if query:
		movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
		return render(request,'web/list.html',{'movies':movies})
	return render(request,'web/list.html',{'movies':movies})


# detail view
def detail(request,movie_id):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	movies = get_object_or_404(Movie,id=movie_id)
	#for rating
	if request.method == "POST":
		rate = request.POST['rating']
		ratingObject = Myrating()
		ratingObject.user   = request.user
		ratingObject.movie  = movies
		ratingObject.rating = rate
		ratingObject.save()
		messages.success(request,"Your Rating is submited ")
		return redirect("index")
	return render(request,'web/detail.html',{'movies':movies})


# Register user
def signUp(request):
	form =UserForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
	context ={
		'form':form
	}
	return render(request,'web/signUp.html',context)				


# Login User
def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
			else:
				return render(request,'web/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'web/login.html',{'error_message': 'Invalid Login'})
	return render(request,'web/login.html')

#Logout user
def Logout(request):
	logout(request)
	return redirect("login")

@csrf_exempt
def mLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    # busUser = BusEmployee.objects.filter(account=user).first()
    # avatar_url=None
    # if busUser is not None:
    #     if busUser.avatar is not None:
    #         avatar_url = busUser.avatar.file_url

    if user is not None:
        #login(request, user)
        token,created=Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key})
    else:
        return HttpResponse(status=400)
@csrf_exempt
def msignUp(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username,password=password)
    if user is None:
        user = User.objects.create_user(username, 'user@gmail.com', password)
        return JsonResponse({'IsSuccess': 1})
    else:
        return JsonResponse({'IsSuccess': 0})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mLogout(request):
	request.user.auth_token.delete()
	logout(request)
	return HttpResponse(status=200)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getListFilm(request):
	type_film = request.POST['type']
	movie_film=[]
	if type_film == "popular":
		movie_list=list(Movie.objects.filter().order_by('id')[:10].values())
	elif type_film == "upcoming":
		movie_list=list(Movie.objects.filter().order_by('-id')[:10].values())
	elif type_film == "intheater":
		movie_list=list(Movie.objects.filter().order_by('id')[20:30].values())

	else:
		df=pd.DataFrame(list(Myrating.objects.all().values()))
		nu=df.user_id.unique().shape[0]
		current_user_id = request.user.id
		if current_user_id>nu:
			movie=Movie.objects.get(id=15)
			q=Myrating(user=request.user,movie=movie,rating=0)
			q.save()

		print("Current user id: ",current_user_id)
		prediction_matrix,Ymean = Myrecommend()
		my_predictions = prediction_matrix[:,current_user_id-1]+Ymean.flatten()
		pred_idxs_sorted = np.argsort(my_predictions)
		pred_idxs_sorted[:] = pred_idxs_sorted[::-1]
		pred_idxs_sorted=pred_idxs_sorted+1
		print(pred_idxs_sorted)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pred_idxs_sorted)])
		movie_list=list(Movie.objects.filter(id__in = pred_idxs_sorted,).order_by(preserved)[:10].values())
	
	return JsonResponse({'listmovie': movie_list})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def searchMovie(request):
	search = request.POST['search']
	movie_list=list(Movie.objects.filter(title__icontains = search).values())
	return JsonResponse({'listmovie': movie_list})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def uploadRating(request):
	rate = request.POST['rating']

	id_movie = request.POST['movie']
	movie=Movie.objects.filter(id=id_movie).first()
	
	ratingObject = Myrating.objects.filter(user=request.user,movie= movie).first()
	print(ratingObject)
	if ratingObject is None:
		ratingObject = Myrating()
		ratingObject.user   = request.user
		ratingObject.movie  = movie
		ratingObject.rating = rate
		ratingObject.save()
		return JsonResponse({"IsSuccess":1})
	else:
		ratingObject.rating = rate
		ratingObject.save()
		return JsonResponse({"IsSuccess":1})





