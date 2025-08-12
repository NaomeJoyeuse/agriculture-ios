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
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() 
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    print("Serializer validation failed:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        # Retrieve user by email
        user = User.objects.get(email=email)

        # Verify the password
        if not check_password(password, user.password):
            return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to both refresh and access tokens
        refresh["user_id"] = user.id
        
        # Get the access token and add the user_id claim
        access_token = refresh.access_token
        access_token["user_id"] = user.id

        # Create response data with tokens and user information
        response_data = {
            "refresh": str(refresh),
            "access": str(access_token),  # Use the modified access token
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "phone_number": user.phone_number,
            },
            "message": "Login successful"
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