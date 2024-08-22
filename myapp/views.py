from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myapp.serializers import *
from myapp.models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def create_custom_user(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"ok","message":"account created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def list_custom_users(request):
    users = CustomUser.objects.all()  
    serializer = CustomUserSerializer(users, many=True, context={'request': request}) 
    return Response({"status":"ok","message":"list users successfully","data":serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def retrieve_custom_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)  
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CustomUserSerializer(user, context={'request': request})  
    return Response({"status":"ok","message":"user retrieved successfully","data":serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_custom_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomUserSerializer(user, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "User updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_custom_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response({"status": "ok", "message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def create_bank_account(request):
    if request.method == 'POST':
        serializer = BankSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"ok","message":"bankaccount Add successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def list_bank_accounts(request):
    if request.method == 'GET':
        bank_accounts = BankAccount.objects.all()
        serializer = BankSerializer(bank_accounts, many=True)
        return Response({"status":"ok","message":"list bank accounts successfully","data":serializer.data})
    


@api_view(['PUT'])
def update_bank_account(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
    except BankAccount.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = BankSerializer(bank_account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"status": "ok", "message": "Bank details updated successfully", "data": serializer.data})


@api_view(['GET'])
def bank_account_detail(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
    except BankAccount.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BankSerializer(bank_account)
        return Response({"status":"ok","message":"account details retrived successfully","data":serializer.data})
    
@api_view(['DELETE'])
def delete_bank_account(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
    except BankAccount.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        bank_account.delete()
        return Response({"status": "ok", "message": "User deleted successfully"},status=status.HTTP_204_NO_CONTENT)

