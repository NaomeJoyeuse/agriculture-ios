
from rest_framework import status
import os
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_fertilizer_plan(request, crop_name):
    crop_key = crop_name.strip().capitalize()  # Ensure correct case format
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(BASE_DIR,'models_db', 'fertlizer.json')
    

    with open(file_path, 'r') as f:
        fertilizer_data = json.load(f)

    plan = fertilizer_data.get(crop_key)

    if plan:
        return Response(plan)
    else:
        return Response({"error": f"No fertilizer data found for '{crop_key}'"}, status=404)