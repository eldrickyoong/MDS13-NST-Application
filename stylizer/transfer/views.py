from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from PIL import Image
from pathlib import Path
import io
from .style_transfer_runner import stylize_image 

def index(request):
    return render(request, "index.html")

def create(request):
    return render(request, "create.html")

def about(request):
    return render(request, "about.html")

def inspiration(request):
    return render(request, "inspiration.html")

def gallery(request):
    return render(request, "gallery.html")

def support(request):
    return render(request, "support.html")


def style_images(request):
    model_name = request.GET.get("model", "johnson_fast_style")
    folder = Path("transfer/static/images") / model_name
    
    try:
        files = [
            f"/static/images/{model_name}/{f.name}"
            for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ]
        return JsonResponse(files, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def stylize(request):
    if request.method == "POST":
        content_file = request.FILES.get("content")
        model_name = request.POST.get("model_name")
        style_file = request.FILES.get("style")
        style_path = request.POST.get("style_path")

        if not content_file:
            return HttpResponse("Missing content image", status=400)
        if not model_name:
            return HttpResponse("Missing model name", status=400)
        if not style_file and not style_path:
            return HttpResponse("Missing style image or style path", status=400)

        result_img = stylize_image(content_file, model_name, style_file, style_path, )

        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        buf.seek(0)
        return FileResponse(buf, content_type="image/png")

    return HttpResponse("Invalid request", status=405)