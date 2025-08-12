# # decorators.py
# import jwt
# from django.http import JsonResponse
# from django.conf import settings
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from functools import wraps

# def jwt_required(view_func):
#     @wraps(view_func)
#     def wrapped_view(request, *args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         print(f"Auth header: {auth_header}")  # Debug line
        
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return JsonResponse({"error": "Authorization token missing or invalid"}, status=401)

#         token = auth_header.split(" ")[1]
#         try:
#             # Validate token and extract user ID
#             access_token = AccessToken(token)
            
#             # Extract user_id from the token payload
#             user_id = access_token.payload.get('user_id')
#             print(f"Extracted user_id: {user_id}")
            
#             if not user_id:
#                 # Fallback to user_id from the token's default payload
#                 user_id = access_token.payload.get('user_id') or access_token.get('user_id')
            
#             if not user_id:
#                 return JsonResponse({"error": "User ID not found in token"}, status=401)
            
#             request.user_id = user_id  # Attach user ID to the request
            
#         except TokenError as e:
#             return JsonResponse({"error": f"Token error: {str(e)}"}, status=401)
#         except InvalidToken:
#             return JsonResponse({"error": "Invalid token"}, status=401)
#         except Exception as e:
#             return JsonResponse({"error": f"Authentication error: {str(e)}"}, status=401)

#         # Proceed to the view if the token is valid
#         return view_func(request, *args, **kwargs)
    
#     return wrapped_view


# decorators.py
from functools import wraps
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

def jwt_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # print(f"Auth header: {auth_header}")  # Debug

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Authorization token missing or invalid"}, status=401)

        token = auth_header.split(" ")[1]
        try:
            access_token = AccessToken(token)
            user_id = access_token.payload.get('user_id')

            if not user_id:
                return JsonResponse({"error": "User ID not found in token"}, status=401)

            # Attach a real user instance so views can use request.user.id
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=401)

            request.user = user
            request.user_id = user.id  # optional

        except (TokenError, InvalidToken) as e:
            return JsonResponse({"error": f"Invalid token: {str(e)}"}, status=401)
        except Exception as e:
            return JsonResponse({"error": f"Authentication error: {str(e)}"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapped_view