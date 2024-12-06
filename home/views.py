from django.shortcuts import render, redirect, get_object_or_404
from home import models
from .forms import READMEForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import markdown2



@login_required
def home(request):
    readme, _ = models.UserProfileREADME.objects.get_or_create(user=request.user)
    # Convert Markdown content to HTML
    readme_html = markdown2.markdown(
        readme.content, 
        extras=["fenced-code-blocks", "tables", "images"]
    )

    user_profile_data, _ = models.UserProfile.objects.get_or_create(user=request.user)
    context={
        'readme_html': readme_html,
        'user_profile_data':user_profile_data,
    }
    print(readme)
    return render(request, 'apps/home/profile.html',context)

from rest_framework import viewsets, permissions
from .models import audio_saving
from .serializers import AudioSavingSerializer

class AudioSavingViewSet(viewsets.ModelViewSet):
    queryset = audio_saving.objects.all()
    serializer_class = AudioSavingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)


from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import SignupSerializer, LoginSerializer

# Signup API
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

# Login API
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token.key
        }, status=status.HTTP_200_OK)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import audio_saving
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

@method_decorator(csrf_exempt, name='dispatch')
class SaveAudioView(View):
    def post(self, request, *args, **kwargs):
        # Get the uploaded audio file
        audio_file = request.FILES.get('audio_file')

        if not audio_file:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

        # Save the audio file to the model
        try:
            # You can save the file using the default storage system or any custom path
            # Here we're saving the file directly using Django's FileField
            audio_instance = audio_saving(user=request.user, audio_file=audio_file)
            audio_instance.save()

            return JsonResponse({
                'message': 'Audio saved successfully',
                'audio_id': audio_instance.id
            })
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Failed to save audio', 'details': str(e)}, status=500)
