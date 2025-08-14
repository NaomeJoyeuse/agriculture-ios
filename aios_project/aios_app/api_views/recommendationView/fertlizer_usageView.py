

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..decorator import jwt_required
from ...serializer.recommendation_serializer import CropRecommendationSerializer
from ...models_db.recommendation import CropRecommendation
from aios_app.models_db.user import User
from aios_app.models_db.input_usage import InputUsage  # adjust path if needed
import os, json

def _fertilizer_json_path():
    """
    Resolve the fertilizer JSON path. Tries both:
    - <project_root>/models_db/fertlizer.json
    - <project_root>/aios_app/models_db/fertlizer.json
    """
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path1 = os.path.join(base, 'models_db', 'fertlizer.json')
    if os.path.exists(path1):
        return path1
    path2 = os.path.join(base, 'aios_app', 'models_db', 'fertlizer.json')
    return path2

@api_view(['GET'])
def get_fertilizer_plan(request, crop_name):
    """
    Returns a fertilizer plan from JSON by crop name.
    URL: /fertilizer/<crop_name>/
    Response: the plan object directly (not wrapped), or 404 if not found.
    """
    crop_raw = (crop_name or '').strip()
    if not crop_raw:
        return Response({"detail": "crop_name is required"}, status=400)

    file_path = _fertilizer_json_path()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            fertilizer_data = json.load(f)
    except Exception as e:
        return Response({"detail": f"Could not read fertilizer file: {e}"}, status=500)

    # Try a few case variants + case-insensitive match
    candidates = [
        crop_raw,
        crop_raw.capitalize(),
        crop_raw.title(),
        crop_raw.lower(),
        crop_raw.upper(),
    ]

    plan = None
    for key in candidates:
        if key in fertilizer_data:
            plan = fertilizer_data[key]
            break
    if plan is None:
        # Last resort: case-insensitive scan
        for k, v in fertilizer_data.items():
            if k.lower() == crop_raw.lower():
                plan = v
                break

    if plan is not None:
        return Response(plan, status=200)
    return Response({"detail": f"No fertilizer data found for '{crop_raw}'"}, status=404)


def _uid(request):
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

@jwt_required
@api_view(['POST'])
def submit_fertilizer_to_agronomist(request):
    data = request.data or {}
    crop_name = (data.get('crop_name') or '').strip()
    farmer_inputs = data.get('farmer_inputs') or {}

    if not crop_name:
        return Response({"detail": "crop_name is required"}, status=400)

    # 0) Resolve user via _uid + fallback to body
    uid = _uid(request) or data.get('user_id')
    user_obj = None
    if uid:
        try:
            user_obj = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": f"user not found for id={uid}"}, status=400)

    # 1) Load fertilizer plan (JSON)
    fertilizer_plan = {}
    try:
        file_path = _fertilizer_json_path()
        with open(file_path, 'r', encoding='utf-8') as f:
            fertilizer_data = json.load(f)
        for key in [crop_name, crop_name.capitalize(), crop_name.title(), crop_name.lower(), crop_name.upper()]:
            if key in fertilizer_data:
                fertilizer_plan = fertilizer_data.get(key) or {}
                break
        if not fertilizer_plan:
            for k, v in fertilizer_data.items():
                if k.lower() == crop_name.lower():
                    fertilizer_plan = v
                    break
    except Exception as e:
        fertilizer_plan = {}
        print(f"[fertilizer] plan load error: {e}")

    # 2) Optional ML usage
    ai_outputs = {}
    if data.get('use_ml'):
        ml_inputs = data.get('ml_inputs') or {}
        try:
            usage = InputUsage.predict_and_save_input_usage(ml_inputs)
            if usage:
                ai_outputs.update({
                    "fertilizer_quantity": usage.fertilizer_quantity,
                    "application_timing": usage.application_timing,
                    "application_method": usage.application_method,
                })
        except Exception as e:
            print(f"[fertilizer] ML predict error: {e}")

    # 3) Build payload for serializer
    payload = {
        "crop_predicted": crop_name,
        "farmer_inputs": {
            **farmer_inputs,
            "crop_name": crop_name,
            # keep audit copy (optional)
            **({"user_id": str(uid)} if uid else {}),
        },
        "ai_outputs": ai_outputs,
        "fertilizer_plan": fertilizer_plan,
    }

    ser = CropRecommendationSerializer(data=payload, context={'request': request})
    if ser.is_valid():
        # Pass user explicitly so it doesn't end up null
        save_kwargs = {"status": "pending_review"}
        if user_obj:
            save_kwargs["user"] = user_obj
        rec = ser.save(**save_kwargs)
        return Response(CropRecommendationSerializer(rec).data, status=201)

    return Response(ser.errors, status=400)