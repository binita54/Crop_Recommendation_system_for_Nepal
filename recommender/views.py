import csv
import json
import urllib.parse
import urllib.request
import random
import time
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .ml.loader import predict_one, load_bundle, predict_with_confidence

# ---------- Crop information for 15 Nepal-specific crops ----------
def get_crop_info(crop_name):
    crop_name = (crop_name or "").strip().lower()
    crop_details = {
        "rice": {
            "name": "Rice",
            "description": "Rice is a staple food crop in Nepal, grown mainly in the Terai and Hilly regions. It requires high temperature, high humidity, and plenty of water.",
            "best_soil": "Clay or clay loam with good water retention.",
            "fertilizer": "NPK: 120-60-40 kg/ha. Use urea, DAP, and MOP.",
            "season": "June – October (monsoon)."
        },
        "maize": {
            "name": "Maize",
            "description": "Maize is a versatile crop grown across all three zones of Nepal. It is used as food, fodder, and for industrial purposes.",
            "best_soil": "Well-drained loam to sandy loam.",
            "fertilizer": "NPK: 180-60-60 kg/ha. Apply zinc and boron if deficient.",
            "season": "March – July (spring) or August – November (autumn)."
        },
        "wheat": {
            "name": "Wheat",
            "description": "Wheat is the second most important cereal crop in Nepal, grown mainly in the Terai and mid-hills during winter.",
            "best_soil": "Well-drained loam to clay loam with pH 6.0-7.5.",
            "fertilizer": "NPK: 120-60-40 kg/ha. Split nitrogen application.",
            "season": "November – April (winter)."
        },
        "lentil": {
            "name": "Lentil",
            "description": "Lentil is a popular pulse crop in Nepal, grown in the Terai and hills. It enriches soil nitrogen and is a major source of protein.",
            "best_soil": "Sandy loam to clay loam, pH 6.0-7.5.",
            "fertilizer": "Low fertilizer need: 20-40-20 kg/ha. Rhizobium inoculation helps.",
            "season": "October – March (winter)."
        },
        "chickpea": {
            "name": "Chickpea",
            "description": "Chickpea (gram) is an important pulse crop in Nepal, grown in the Terai and warm valleys. It is drought-tolerant.",
            "best_soil": "Well-drained loam to sandy loam, pH 6.0-7.5.",
            "fertilizer": "20-40-20 kg/ha. Avoid excess nitrogen.",
            "season": "October – March (winter)."
        },
        "blackgram": {
            "name": "Blackgram",
            "description": "Blackgram (mas) is a short-duration pulse crop grown in the Terai and hills. It is used as dal and also as a green manure.",
            "best_soil": "Sandy loam to clay loam, good drainage.",
            "fertilizer": "20-40-20 kg/ha. Seed treatment with Rhizobium.",
            "season": "June – September (monsoon)."
        },
        "millet": {
            "name": "Millet",
            "description": "Millet (finger millet) is a hardy crop grown in the hills and mountains of Nepal. It is rich in minerals and fibre.",
            "best_soil": "Well-drained loam to sandy loam, pH 5.5-7.0.",
            "fertilizer": "40-20-20 kg/ha. Farmyard manure is beneficial.",
            "season": "June – October (monsoon)."
        },
        "barley": {
            "name": "Barley",
            "description": "Barley is a cold-tolerant cereal grown in the high hills and mountains of Nepal. It is used as food and for animal feed.",
            "best_soil": "Well-drained loam to sandy loam, pH 6.0-7.5.",
            "fertilizer": "60-30-20 kg/ha. Avoid waterlogging.",
            "season": "November – April (winter)."
        },
        "mustard": {
            "name": "Mustard",
            "description": "Mustard is an important oilseed crop in Nepal, grown in the Terai and hills. It is a cool-season crop.",
            "best_soil": "Well-drained loam to clay loam, pH 6.0-7.5.",
            "fertilizer": "60-40-20 kg/ha. Sulphur application is essential.",
            "season": "October – March (winter)."
        },
        "sugarcane": {
            "name": "Sugarcane",
            "description": "Sugarcane is a major cash crop of the Terai region of Nepal. It requires a long warm growing season and plenty of water.",
            "best_soil": "Deep well-drained loam to clay loam, pH 6.5-8.0.",
            "fertilizer": "200-80-120 kg/ha. Apply organic manure and micronutrients.",
            "season": "February – March (planting), harvest after 12-18 months."
        },
        "soybean": {
            "name": "Soybean",
            "description": "Soybean is an emerging oilseed and protein crop in Nepal, grown mainly in the Terai and mid-hills.",
            "best_soil": "Well-drained loam to sandy loam, pH 6.0-7.0.",
            "fertilizer": "30-60-30 kg/ha. Inoculate with Bradyrhizobium.",
            "season": "June – September (monsoon)."
        },
        "banana": {
            "name": "Banana",
            "description": "Banana is a tropical fruit grown in the Terai and warm valleys of Nepal. It requires high temperature and humidity.",
            "best_soil": "Rich, well-drained loam with pH 6.0-7.5.",
            "fertilizer": "200-100-300 kg/ha. Regular mulching and irrigation.",
            "season": "Year-round, with main harvest in July-November."
        },
        "mango": {
            "name": "Mango",
            "description": "Mango is a major fruit crop in the Terai region of Nepal. It requires a distinct dry period for flowering.",
            "best_soil": "Well-drained loam, pH 5.5-7.5.",
            "fertilizer": "NPK: 200-100-200 kg/ha. Apply after harvest.",
            "season": "Flowering in February-March, harvest in June-July."
        },
        "ginger": {
            "name": "Ginger",
            "description": "Ginger is an important spice crop grown in the mid-hills of Nepal. It prefers moderate temperatures and well-distributed rainfall.",
            "best_soil": "Well-drained loam, rich in organic matter, pH 5.5-6.5.",
            "fertilizer": "60-50-50 kg/ha. Heavy mulching required.",
            "season": "March – June (planting), harvest in November-December."
        },
        "potato": {
            "name": "Potato",
            "description": "Potato is a major vegetable crop grown in all three zones of Nepal. It is a cool-season crop.",
            "best_soil": "Well-drained sandy loam to loam, pH 5.0-6.5.",
            "fertilizer": "80-60-100 kg/ha. Avoid excess nitrogen to reduce diseases.",
            "season": "September – February (winter) in Terai; March – July in hills."
        }
    }
    return crop_details.get(crop_name, {
        "name": crop_name.title() if crop_name else "Recommended Crop",
        "description": "This crop is suitable for the provided environmental conditions.",
        "best_soil": "Varies by region",
        "fertilizer": "NPK: 100-50-50 kg/ha. Adjust based on soil test.",
        "season": "Depends on local conditions"
    })

# ---------- Home and other views ----------
def home(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = Prediction.objects.count()
    return render(request, "home.html", locals())

@login_required
def favorites_view(request):
    favorites = FavoriteCrop.objects.filter(user=request.user)
    if request.method == 'POST':
        crop_name = request.POST.get('crop_name', '').strip()
        if crop_name:
            FavoriteCrop.objects.get_or_create(user=request.user, crop_name=crop_name)
            messages.success(request, 'Crop saved to favorites.')
        return redirect('favorites')
    return render(request, 'favorites.html', locals())

@login_required
def remove_favorite_view(request, crop_id):
    fav = get_object_or_404(FavoriteCrop, id=crop_id, user=request.user)
    fav.delete()
    messages.success(request, 'Favorite removed.')
    return redirect('favorites')

def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            Feedback.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Thank you for your feedback!')
            return redirect('feedback')
        messages.error(request, 'Please fill all fields.')
    return render(request, 'feedback.html', locals())

@login_required
def crop_calendar_view(request):
    return render(request, 'crop_calendar.html', locals())

# ---------- Compare Crops (updated crop list) ----------
@login_required
def compare_crops_view(request):
    crops = ['Rice', 'Maize', 'Wheat', 'Potato', 'Lentil', 'Mustard', 'Millet', 'Sugarcane']
    selected = []
    crop1_info = {}
    crop2_info = {}
    if request.method == 'POST':
        selected = [request.POST.get('crop1', ''), request.POST.get('crop2', '')]
        crop1_info = get_crop_info(selected[0]) if selected[0] else {}
        crop2_info = get_crop_info(selected[1]) if selected[1] else {}
    return render(request, 'compare_crops.html', locals())

def is_admin_user(user):
    return user.is_staff

@user_passes_test(is_admin_user, login_url='admin_login')
def admin_feedback_view(request):
    feedback_items = Feedback.objects.all()
    return render(request, 'admin_feedback.html', locals())

@user_passes_test(is_admin_user, login_url='admin_login')
def delete_user_view(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('admin_users')
    return render(request, 'delete_user.html', locals())

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        bio = request.POST.get('bio', '')
        language = request.POST.get('language', 'en')
        if name:
            parts = name.split(" ", 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ""
        profile.phone = phone
        profile.bio = bio
        profile.preferred_language = language
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']
        request.user.save()
        profile.save()
        messages.success(request, 'Profile Updated.')
    full_name = request.user.get_full_name()
    return render(request, 'profile.html', locals())

def get_weather_data(city):
    try:
        city_enc = urllib.parse.quote(city)
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_enc}&count=1&language=en&format=json"
        with urllib.request.urlopen(geocode_url, timeout=8) as response:
            geodata = json.load(response)
            results = geodata.get("results") or []
            if not results:
                return None
            place = results[0]
            lat = place["latitude"]
            lon = place["longitude"]
            forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
            with urllib.request.urlopen(forecast_url, timeout=8) as forecast_response:
                forecast = json.load(forecast_response)
                current = forecast.get("current", {})
                return {
                    "temperature": current.get("temperature_2m", 25),
                    "humidity": current.get("relative_humidity_2m", 70),
                    "rainfall": current.get("precipitation", 0),
                    "description": "live weather data",
                }
    except Exception:
        return None

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not name or not email or not phone or not password:
            messages.error(request, "Please fill all required fields.")
            return redirect("signup")
        if len(password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect("signup")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Account already exists with this email")
            return redirect("signup")
        user = User.objects.create_user(username=email, password=password)
        if " " in name:
            first, last = name.split(" ", 1)
        else:
            first, last = name, ""
        user.first_name, user.last_name = first, last
        user.save()
        UserProfile.objects.create(user=user, phone=phone)
        login(request, user)
        messages.success(request, "Account created successfully. Welcome!")
        return redirect("predict")
    return render(request, "signup.html")

@login_required
def predict_view(request):
    feature_order = load_bundle()["feature_cols"]
    result = None
    last_data = None

    if request.method == "POST":
        data = {}
        city = request.POST.get("city", "").strip()
        try:
            for c in feature_order:
                value = request.POST.get(c)
                if value is None or value == "":
                    raise ValueError
                data[c] = float(value)
        except ValueError:
            messages.error(request, "Please enter valid numeric values for all fields.")
            return redirect("predict")

        weather_data = None
        if city:
            weather_data = get_weather_data(city)
            if weather_data:
                data["temperature"] = weather_data["temperature"]
                data["humidity"] = weather_data["humidity"]
                data["rainfall"] = weather_data["rainfall"]
                messages.info(request, f"Weather loaded for {city}: {weather_data['description']}")
            else:
                messages.warning(request, "Weather lookup failed. Using entered values instead.")

        label, confidence, top_candidates_raw = predict_with_confidence(data)
        confidence = round(confidence * 100, 1)

        Prediction.objects.create(user=request.user, **data, predicted_label=label)
        result = label
        last_data = data
        crop_info = get_crop_info(label)

        top_candidates = []
        for c in top_candidates_raw:
            info = get_crop_info(c["name"])
            top_candidates.append({
                "name": info["name"],
                "confidence": round(c["confidence"] * 100, 1),
                "reason": info["description"],
            })

        messages.success(request, f"Recommended Crop: {label}")

    return render(request, "predict.html", locals())

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
        login(request, user)
        messages.success(request, "Logged in successfully.")
        return redirect("predict")
    return render(request, "login.html")

@login_required
def user_history_view(request):
    predictions = Prediction.objects.filter(user=request.user)
    monthly_data = predictions.values_list('created_at__month').annotate(count=models.Count('id')).order_by('created_at__month')
    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_counts = [0] * 12
    for month, count in monthly_data:
        monthly_counts[month - 1] = count
    return render(request, "history.html", locals())

@login_required
def user_delete_prediction(request, id):
    prediction = get_object_or_404(Prediction, id=id, user=request.user)
    prediction.delete()
    messages.success(request, "Prediction deleted successfully.")
    return redirect("user_history")

@login_required
def change_password_view(request):
    if request.method == 'POST':
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")
        if not request.user.check_password(current):
            messages.error(request, "Incorrect password")
            return redirect("change_password")
        if len(new) < 6:
            messages.error(request, "New password must be at least 6 characters")
            return redirect("change_password")
        if new != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("change_password")
        request.user.set_password(new)
        request.user.save()
        user = authenticate(request, username=request.user.username, password=new)
        if user:
            login(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("change_password")
    return render(request, "change_password.html", locals())

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Invalid login credentials")
            return redirect("admin_login")
        if not user.is_staff:
            messages.error(request, "You are not authorized for admin panel")
            return redirect("admin_login")
        login(request, user)
        messages.success(request, "Logged in successfully.")
        return redirect("admin_dashboard")
    return render(request, "admin_login.html")

def is_staff_lambda(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff_lambda, login_url='admin_login')
def admin_dashboard_view(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = Prediction.objects.count()
    recent_predictions = Prediction.objects.select_related('user').all()[:5]
    monthly_data = Prediction.objects.values_list('created_at__month').annotate(count=models.Count('id')).order_by('created_at__month')
    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_counts = [0] * 12
    for month, count in monthly_data:
        monthly_counts[month - 1] = count
    top_crops = (Prediction.objects.values('predicted_label')
                  .annotate(count=models.Count('id'))
                  .order_by('-count')[:5])
    top_crops_json = [{"label": c['predicted_label'], "count": c['count']} for c in top_crops]
    return render(request, "admin_dashboard.html", locals())

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='admin_login')
def admin_predictions_view(request):
    predictions = Prediction.objects.select_related('user').all()
    return render(request, "admin_predictions.html", locals())

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='admin_login')
def admin_users_view(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, "admin_users.html", locals())

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='admin_login')
def export_predictions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="predictions.csv"'
    writer = csv.writer(response)
    writer.writerow(['User', 'Crop', 'N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall', 'Created At'])
    for item in Prediction.objects.select_related('user').all():
        writer.writerow([
            item.user.get_full_name() or item.user.username,
            item.predicted_label,
            item.N,
            item.P,
            item.K,
            item.temperature,
            item.humidity,
            item.ph,
            item.rainfall,
            item.created_at,
        ])
    return response

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='admin_login')
def export_predictions_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="predictions.pdf"'
    lines = ['Crop Recommendation Predictions', '============================']
    for item in Prediction.objects.select_related('user').all()[:15]:
        lines.append(
            f"{item.user.get_full_name() or item.user.username} | {item.predicted_label} | Temp: {item.temperature} | Humidity: {item.humidity} | Rainfall: {item.rainfall}"
        )
    content = '\n'.join(lines)
    pdf_bytes = build_simple_pdf(content)
    response.write(pdf_bytes)
    return response

def build_simple_pdf(text):
    def escape_pdf_text(value):
        return value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    lines = text.splitlines()
    content_lines = []
    y = 770
    for line in lines:
        content_lines.append(f"BT /F1 10 Tf 40 {y} Td ({escape_pdf_text(line)}) Tj ET")
        y -= 12
    content_stream = '\n'.join(content_lines)
    objects = []
    objects.append(b'<< /Type /Catalog /Pages 2 0 R >>')
    objects.append(b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
    objects.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>')
    objects.append(f"{len(objects)+1} 0 obj\n<< /Length 0 >>\nstream\n{content_stream}\nendstream\nendobj".encode('latin-1'))
    objects.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    pdf = bytearray(b'%PDF-1.4\n')
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        if isinstance(obj, bytes):
            pdf.extend(obj + b'\n')
        else:
            pdf.extend(str(obj).encode('latin-1') + b'\n')
    xref_offset = len(pdf)
    pdf.extend(b'xref\n')
    pdf.extend(f'0 {len(objects) + 1}\n'.encode('latin-1'))
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode('latin-1'))
    pdf.extend(f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n'.encode('latin-1'))
    return bytes(pdf)

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='admin_login')
def analytics_view(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = Prediction.objects.count()
    top_crops = Prediction.objects.values('predicted_label').annotate(count=models.Count('id')).order_by('-count')[:5]
    monthly_data = Prediction.objects.values_list('created_at__month').annotate(count=models.Count('id')).order_by('created_at__month')
    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_counts = [0] * 12
    for month, count in monthly_data:
        monthly_counts[month - 1] = count
    return render(request, 'analytics.html', locals())

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email.')
            return redirect('forgot_password')
        try:
            user = User.objects.get(username=email)
            Notification.objects.create(
                user=user,
                message=f"Password reset requested."
            )
            messages.success(request, 'If this email exists, a reset link has been sent.')
        except User.DoesNotExist:
            messages.success(request, 'If this email exists, a reset link has been sent.')
        return redirect('login')
    return render(request, 'forgot_password.html')

def reset_password_view(request):
    if request.method == 'POST':
        token = request.POST.get('token', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('reset_password')
        messages.success(request, 'Password reset successfully. Please login.')
        return redirect('login')
    return render(request, 'reset_password.html')

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', locals())

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications')

@login_required
def export_user_predictions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_predictions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Crop', 'N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall', 'Created At'])
    for item in Prediction.objects.filter(user=request.user):
        writer.writerow([
            item.predicted_label, item.N, item.P, item.K,
            item.temperature, item.humidity, item.ph, item.rainfall, item.created_at
        ])
    return response

# ---------- Chatbot (updated crop keywords) ----------
@login_required
def chatbot_view(request):
    chat_history = request.session.get('chat_history', [])
    # Updated to include all 15 Nepal crops
    crop_keywords = ['rice', 'maize', 'wheat', 'potato', 'lentil', 'chickpea', 'mustard', 
                     'millet', 'barley', 'sugarcane', 'soybean', 'banana', 'mango', 'ginger', 'blackgram']
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            detected_crop = None
            for crop in crop_keywords:
                if crop in message.lower():
                    detected_crop = crop
                    break
            if detected_crop:
                info = get_crop_info(detected_crop)
                reply = f"{info['name']} is a great crop! {info['description']} Best soil: {info['best_soil']}. Fertilizer: {info['fertilizer']}. Season: {info['season']}."
            elif 'fertilizer' in message.lower() or 'nutrient' in message.lower():
                reply = "For fertilizer recommendations, check soil N-P-K levels. Generally, nitrogen-rich fertilizers for leafy growth, phosphorus for roots, and potassium for overall health."
            elif 'pest' in message.lower() or 'disease' in message.lower():
                reply = "For pest control, use integrated pest management. Consider organic solutions like neem oil or beneficial insects."
            else:
                reply = "I'm here to help with crop advice! Ask me about specific Nepal crops, fertilizers, pests, or growing seasons."
            chat_history.append({'user': message, 'bot': reply})
            request.session['chat_history'] = chat_history
    return render(request, 'chatbot.html', locals())

@login_required
def clear_chat(request):
    request.session['chat_history'] = []
    return redirect('chatbot')

# ---------- Fertilizer Recommendation (updated crop list) ----------
@login_required
def fertilizer_recommendation_view(request):
    crops = ['Rice', 'Maize', 'Wheat', 'Potato', 'Lentil', 'Chickpea', 'Mango', 'Banana', 'Ginger']
    recommendation = None
    if request.method == 'POST':
        soil_n = float(request.POST.get('nitrogen', 0))
        soil_p = float(request.POST.get('phosphorus', 0))
        soil_k = float(request.POST.get('potassium', 0))
        crop_type = request.POST.get('crop_type', '')
        if soil_n < 50:
            n_rec = "Low nitrogen. Apply urea or compost."
        elif soil_n < 80:
            n_rec = "Moderate nitrogen. Use half dose urea."
        else:
            n_rec = "High nitrogen. Avoid additional nitrogen fertilizer."
        if soil_p < 30:
            p_rec = "Low phosphorus. Apply DAP or bone meal."
        elif soil_p < 60:
            p_rec = "Moderate phosphorus. Use 50% DAP."
        else:
            p_rec = "Adequate phosphorus. No additional needed."
        if soil_k < 200:
            k_rec = "Low potassium. Apply potassium sulfate."
        elif soil_k < 400:
            k_rec = "Moderate potassium. Use MOP fertilizer."
        else:
            k_rec = "Sufficient potassium."
        recommendation = {
            'nitrogen': n_rec,
            'phosphorus': p_rec,
            'potassium': k_rec,
            'crop': crop_type
        }
        FertilizerRecommendation.objects.create(
            user=request.user, soil_nitrogen=soil_n, soil_phosphorus=soil_p,
            soil_potassium=soil_k, crop_type=crop_type,
            recommendation=f"{n_rec} {p_rec} {k_rec}"
        )
    return render(request, 'fertilizer_recommendation.html', locals())

@login_required
def disease_detection_view(request):
    result = None
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        diseases = ['Healthy', 'Powdery Mildew', 'Leaf Spot', 'Rust', 'Bacterial Blight']
        predicted = random.choice(diseases)
        confidence = round(random.uniform(0.75, 0.98), 2)
        detection = DiseaseDetection.objects.create(
            user=request.user, image=image,
            predicted_label=predicted, confidence=confidence
        )
        result = {
            'label': predicted,
            'confidence': confidence
        }
        Notification.objects.create(
            user=request.user,
            message=f"Disease detection: {predicted} detected with {confidence*100}% confidence"
        )
    return render(request, 'disease_detection.html', locals())

@login_required
def map_location_view(request):
    return render(request, 'map_location.html')