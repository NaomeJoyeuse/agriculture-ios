from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from aios_app.serializer.user_serializer import UserSerializer
from aios_app.models_db.user import User
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from aios_app.api_views.decorator import jwt_required
from rest_framework import status as drf_status
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() 
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    print("Serializer validation failed:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def login(request):
#     email = request.data.get('email')
#     password = request.data.get('password')

#     try:
#         # Retrieve user by email
#         user = User.objects.get(email=email)

#         # Verify the password
#         if not check_password(password, user.password):
#             return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)
        
#         # Add custom claims to both refresh and access tokens
#         refresh["user_id"] = user.id
        
#         # Get the access token and add the user_id claim
#         access_token = refresh.access_token
#         access_token["user_id"] = user.id

#         # Create response data with tokens and user information
#         response_data = {
#             "refresh": str(refresh),
#             "access": str(access_token),  # Use the modified access token
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": user.role,
#                 "phone_number": user.phone_number,
#             },
#             "message": "Login successful"
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except User.DoesNotExist:
#         return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)

        if not check_password(password, user.password):
            return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Determine account status. Prefer `status` field, fallback to `is_active`.
        status_value = getattr(user, "status", None)
        if status_value is None:
            status_value = "active" if getattr(user, "is_active", True) else "inactive"
        status_value = str(status_value).lower()

        # Block non-active accounts at login (farmer or any role if you want)
        if status_value != "active":
            return Response(
                {
                    "error": "Your account is suspended. Please contact your cooperative leader.",
                    "code": "ACCOUNT_SUSPENDED",
                    "status": status_value,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens (only for active accounts)
        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id

        access_token = refresh.access_token
        access_token["user_id"] = user.id

        response_data = {
            "refresh": str(refresh),
            "access": str(access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "phone_number": user.phone_number,
                "status": status_value,   # for completeness
                "is_active": True,        # normalize for frontends that expect this
            },
            "message": "Login successful",
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@jwt_required 
def list_users(request):
    """
    Get a list of all users.
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@jwt_required 
def get_user_by_id(request, user_id):
    """
    Get a single user by ID.
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@jwt_required
def update_user_status(request, user_id):
    """
    Update a user's account status.
    Supports:
      - status: "active" | "inactive" | "suspended"  (if your model has a CharField `status`)
      - is_active: true | false                      (if your model uses a BooleanField `is_active`)

    Only 'admin' and 'leader' are allowed to update statuses.
    """
    # Permission check
    actor = getattr(request, "user", None)
    actor_role = getattr(actor, "role", None)
    # if actor_role not in ("admin", "leader"):
    #     return Response({"error": "Permission denied"}, status=drf_status.HTTP_403_FORBIDDEN)

    # Load target user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=drf_status.HTTP_404_NOT_FOUND)

    # Optional extra guardrails
    if user.role == "admin" and actor_role != "admin":
        return Response({"error": "Only admins can change admin accounts"}, status=drf_status.HTTP_403_FORBIDDEN)
    if actor and getattr(actor, "id", None) == user.id:
        # Avoid locking yourself out
        return Response({"error": "You cannot change your own account status"}, status=drf_status.HTTP_400_BAD_REQUEST)

    # Update status
    status_value = request.data.get("status", None)
    is_active_value = request.data.get("is_active", None)

    if status_value is not None:
        allowed = {"active", "inactive", "suspended"}
        status_value = str(status_value).lower()
        if status_value not in allowed:
            return Response({"error": "Invalid status", "allowed": sorted(list(allowed))},
                            status=drf_status.HTTP_400_BAD_REQUEST)
        # Requires you added a CharField `status` on User
        user.status = status_value
        user.save(update_fields=["status"])

    elif is_active_value is not None:
        # Requires you added BooleanField `is_active` on User
        val = str(is_active_value).strip().lower()
        truthy = val in ("1", "true", "yes", "on")
        user.is_active = truthy
        user.save(update_fields=["is_active"])

    else:
        return Response({"error": 'Provide "status" or "is_active" payload'},
                        status=drf_status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=drf_status.HTTP_200_OK)