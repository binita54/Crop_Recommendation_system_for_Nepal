from django.contrib import admin
from .models import UserProfile, Prediction, FavoriteCrop, Feedback, Notification, DiseaseDetection, FertilizerRecommendation

admin.site.register(UserProfile)
admin.site.register(Prediction)
admin.site.register(FavoriteCrop)
admin.site.register(Feedback)
admin.site.register(Notification)
admin.site.register(DiseaseDetection)
admin.site.register(FertilizerRecommendation)
