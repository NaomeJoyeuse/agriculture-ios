
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...api_views.decorator import jwt_required
from ...models_db.feedback import Feedback
from ...serializer.feedback_serializer import FeedbackSerializer

User = get_user_model()

# Helpers
def _uid(request):
    # Works if jwt_required sets request.user and/or request.user_id
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

def _role(user):
    return str(getattr(user, 'role', '')).lower()

def _is_admin_or_leader(user):
    return _role(user) in ('admin', 'leader')

def _is_farmer_or_supplier(user):
    return _role(user) in ('farmer', 'supplier')

def _paginate(request, qs):
    try:
        page = max(1, int(request.query_params.get("page", 1)))
    except Exception:
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", 20))
        page_size = max(1, min(page_size, 100))
    except Exception:
        page_size = 20

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    return qs[start:end], {
        "count": total,
        "page": page,
        "page_size": page_size,
        "has_next": end < total,
        "has_prev": start > 0,
    }

# ========================
# GET: My feedback (owner)
# ========================
@jwt_required
@api_view(['GET'])
def my_feedback_list(request):
    uid = _uid(request)
    if not uid:
        return Response({'detail': 'Authentication required'}, status=401)

    qs = Feedback.objects.select_related("user").filter(user_id=uid)

    status_val = request.query_params.get("status")
    if status_val:
        qs = qs.filter(status=str(status_val).lower())

    q = (request.query_params.get("q") or "").strip()
    if q:
        qs = qs.filter(content__icontains=q)

    page_qs, meta = _paginate(request, qs)
    data = FeedbackSerializer(page_qs, many=True).data
    return Response({"results": data, "meta": meta}, status=200)

# ====================================
# GET: All feedback (admin/leader only)
# ====================================
@jwt_required
@api_view(['GET'])
def list_feedbacks(request):
    user = getattr(request, 'user', None)
    if not user:
        return Response({'detail': 'Authentication required'}, status=401)

    if not _is_admin_or_leader(user):
        return Response({'detail': 'Permission denied'}, status=403)

    qs = Feedback.objects.select_related("user").all()

    status_val = request.query_params.get("status")
    if status_val:
        qs = qs.filter(status=str(status_val).lower())

    role_val = request.query_params.get("role")
    if role_val:
        qs = qs.filter(user__role=str(role_val).lower())

    q = (request.query_params.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(content__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q)
        )

    page_qs, meta = _paginate(request, qs)
    data = FeedbackSerializer(page_qs, many=True).data
    return Response({"results": data, "meta": meta}, status=200)

# ============================================
# GET: Feedback detail (owner or admin/leader)
# ============================================
@jwt_required
@api_view(['GET'])
def get_feedback(request, feedback_id):
    uid = _uid(request)
    if not uid:
        return Response({'detail': 'Authentication required'}, status=401)

    user = getattr(request, 'user', None)

    try:
        fb = Feedback.objects.select_related("user").get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({'detail': 'Feedback not found'}, status=404)

    if not (_is_admin_or_leader(user) or fb.user_id == uid):
        return Response({'detail': 'Permission denied'}, status=403)

    return Response(FeedbackSerializer(fb).data, status=200)

# ================================
# POST: Create (farmer/supplier)
# ================================
@jwt_required
@api_view(["POST"])
def create_feedback(request):
    """
    Create feedback using the client-sent user (or user_id).
    - Farmers/Suppliers: can only submit for themselves.
    - Admins/Leaders: can submit for any existing user.
    """
    requester = getattr(request, "user", None)
    if not requester:
        return Response({"detail": "Authentication required"}, status=401)

    content = (request.data.get("content") or "").strip()
    if not content:
        return Response({"detail": "Content is required"}, status=400)

    # Accept either 'user' or 'user_id' from client and resolve to a PK
    raw_uid = request.data.get("user")
    if raw_uid in (None, "", "null"):
        raw_uid = request.data.get("user_id")

    if raw_uid in (None, "", "null"):
        return Response({"user": ["This field may not be null."]}, status=400)

    try:
        target_uid = int(raw_uid)
    except Exception:
        return Response({"user": ["A valid integer is required."]}, status=400)

    # Role-based rule: farmers/suppliers can only submit for themselves
    if _is_farmer_or_supplier(requester) and requester.id != target_uid:
        return Response({"detail": "You can only submit feedback for your own account."}, status=403)

    # Ensure target user exists
    try:
        User.objects.get(id=target_uid)
    except User.DoesNotExist:
        return Response({"user": ["User not found."]}, status=404)

    # Prepare serializer payload with 'user' field (PK)
    data = {
        "user": target_uid,    # serializer expects 'user' (PK), not 'user_id'
        "content": content,
        # status/response are read-only during creation
    }

    ser = FeedbackSerializer(data=data, context={"request": request})
    if ser.is_valid():
        fb = ser.save()  # status defaults to 'new'
        return Response(FeedbackSerializer(fb).data, status=201)
    return Response(ser.errors, status=400)
# Optional alias using direct create
@jwt_required
@api_view(['POST'])
def submit_feedback(request):
    user = getattr(request, 'user', None)
    if not user:
        return Response({'detail': 'Authentication required'}, status=401)

    if not _is_farmer_or_supplier(user):
        return Response({'detail': 'Only farmers or suppliers can submit feedback'}, status=403)

    content = (request.data.get("content") or "").strip()
    if not content:
        return Response({'detail': 'Content is required'}, status=400)

    fb = Feedback.objects.create(user_id=user.id, content=content)
    return Response(FeedbackSerializer(fb).data, status=201)

# =======================================================
# PATCH: Update (admin/leader: status/response; owner: content if 'new')
# =======================================================
@jwt_required
@api_view(['PATCH'])
def update_feedback(request, feedback_id):
    user = getattr(request, 'user', None)
    uid = _uid(request)
    if not uid or not user:
        return Response({'detail': 'Authentication required'}, status=401)

    try:
        fb = Feedback.objects.select_related("user").get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({'detail': 'Feedback not found'}, status=404)

    is_owner = (fb.user_id == uid)
    is_admin_leader = _is_admin_or_leader(user)

    # Admin/Leader updates
    if is_admin_leader:
        allowed_status = {"new", "reviewed", "responded"}
        updated = False

        if "status" in request.data:
            new_status = str(request.data.get("status", "")).lower()
            if new_status not in allowed_status:
                return Response({'detail': 'Invalid status', 'allowed': sorted(list(allowed_status))}, status=400)
            fb.status = new_status
            updated = True

        if "response" in request.data:
            fb.response = request.data.get("response")
            updated = True

        if not updated:
            return Response({'detail': 'Provide status and/or response to update'}, status=400)

        fb.save()
        return Response(FeedbackSerializer(fb).data, status=200)

    # Owner can edit content if feedback is still 'new'
    if is_owner and fb.status == "new":
        new_content = (request.data.get("content") or "").strip()
        if not new_content:
            return Response({'detail': 'Content is required'}, status=400)
        fb.content = new_content
        fb.save(update_fields=["content"])
        return Response(FeedbackSerializer(fb).data, status=200)

    return Response({'detail': 'Permission denied'}, status=403)

# ================================
# PATCH: Owner content-only update
# ================================
@jwt_required
@api_view(['PATCH'])
def update_my_feedback(request, feedback_id):
    uid = _uid(request)
    if not uid:
        return Response({'detail': 'Authentication required'}, status=401)

    try:
        fb = Feedback.objects.get(id=feedback_id, user_id=uid)
    except Feedback.DoesNotExist:
        return Response({'detail': 'Feedback not found'}, status=404)

    if fb.status != "new":
        return Response({'detail': 'Can only edit feedback with status "new"'}, status=400)

    new_content = (request.data.get("content") or "").strip()
    if not new_content:
        return Response({'detail': 'Content is required'}, status=400)

    fb.content = new_content
    fb.save(update_fields=['content'])
    return Response(FeedbackSerializer(fb).data, status=200)

# ================================
# DELETE: Admin/Leader only
# ================================
@jwt_required
@api_view(['DELETE'])
def delete_feedback(request, feedback_id):
    user = getattr(request, 'user', None)
    if not user:
        return Response({'detail': 'Authentication required'}, status=401)

    if not _is_admin_or_leader(user):
        return Response({'detail': 'Only admin or leader can delete feedback'}, status=403)

    try:
        fb = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({'detail': 'Feedback not found'}, status=404)

    fb.delete()
    return Response({'detail': 'Feedback deleted'}, status=204)