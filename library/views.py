from django.http import JsonResponse

def api_overview(request):
    return JsonResponse({
        "message": "API is working!",
        "endpoints": {
        }
    })