from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myapp.serializers import *
from myapp.models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import load_model
from decimal import Decimal
import random


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
def create_bank_account(request, user_id):
    if request.method == 'POST':
        # Attach the user_id to the incoming data
        data = request.data.copy()
        data['user_id'] = user_id

        serializer = BankSerializer(data=data)
        if serializer.is_valid():
            bank_account = serializer.save()  # Save the bank account and store the instance
            return Response({
                "status": "ok",
                "message": "Bank account added successfully",
                "data": {
                    "id": bank_account.id,  # Include the ID of the newly created bank account
                    **serializer.data  # Include the rest of the serialized data
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_bank_accounts(request, user_id):
    if request.method == 'GET':
        # Retrieve all bank accounts associated with the user_id
        bank_accounts = BankAccount.objects.filter(user_id=user_id)
        serializer = BankSerializer(bank_accounts, many=True)
        return Response({
            "status": "ok",
            "message": "Bank accounts retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
def update_bank_account(request, user_id, account_id):
    try:
        # Retrieve the specific bank account associated with the user_id and account_id
        bank_account = BankAccount.objects.get(user_id=user_id, id=account_id)
    except BankAccount.DoesNotExist:
        return Response({"status": "error", "message": "Bank account not found"}, status=status.HTTP_404_NOT_FOUND)

    # Partial updates are allowed with PATCH; full updates are expected with PUT
    serializer = BankSerializer(bank_account, data=request.data, partial=(request.method == 'PATCH'))

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "ok",
            "message": "Bank account updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def bank_account_detail(request, user_id, account_id):
    try:
        # Retrieve the specific bank account associated with the user_id and account_id
        bank_account = BankAccount.objects.get(user_id=user_id, id=account_id)
    except BankAccount.DoesNotExist:
        return Response({"status": "error", "message": "Bank account not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the bank account details
    serializer = BankSerializer(bank_account)
    return Response({
        "status": "ok",
        "message": "Bank account retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)




@api_view(['POST'])
def create_transaction(request, user_id):
    # Add the user_id to the incoming data
    data = request.data.copy()
    data['user_id'] = user_id

    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        # Extract the provided amount
        amount = serializer.validated_data['amount']
        
        # Convert amount to Decimal if it's not already
        amount = Decimal(str(amount))

        # Generate random values for oldbalanceOrg based on provided examples
        oldbalanceOrg_choices = [
            Decimal('170136.0'), Decimal('21249.0'), Decimal('181.0'), 
            Decimal('23647.0'), Decimal('106071.0')
        ]
        oldbalanceOrg = random.choice(oldbalanceOrg_choices)
        
        # Generate random values for oldbalanceDest based on provided examples
        oldbalanceDest_choices = [
            Decimal('0.0'), Decimal('21182.0'), Decimal('173527.1'),
            Decimal('110696.18'), Decimal('0.0')
        ]
        oldbalanceDest = random.choice(oldbalanceDest_choices)

        # Check if the amount is greater than the old balance
        if amount > oldbalanceOrg:
            return Response({
                'status': 'error',
                'message': 'Insufficient balance for this transaction.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate new balances after the transaction
        newbalanceOrig = oldbalanceOrg - amount  # Both are Decimal
        newbalanceDest = oldbalanceDest + amount  # Both are Decimal

        # Load the logistic regression model
        model = load_model()

        # Prepare the features for fraud detection
        features = [
            float(amount),          # Amount of the transaction
            float(oldbalanceOrg),   # Balance before the transaction
            float(newbalanceOrig),  # New balance after the transaction
            float(oldbalanceDest),  # Initial balance of recipient before the transaction
            float(newbalanceDest),  # New balance of recipient after the transaction
            float(serializer.validated_data.get('isFlaggedFraud', 0.0))  # Include isFlaggedFraud
        ]

        # Predict whether the transaction is fraudulent
        prediction = model.predict([features])
        is_fraud = bool(prediction[0])

        # Save the transaction with the calculated fields and user_id
        transaction = serializer.save(
            oldbalanceOrg=oldbalanceOrg,
            newbalanceOrig=newbalanceOrig,
            oldbalanceDest=oldbalanceDest,
            newbalanceDest=newbalanceDest,
            is_fraud=is_fraud,
            isFlaggedFraud=0.0  # Set default value for isFlaggedFraud
        )

        return Response({
            'transaction_id': transaction.id,
            'amount': amount,
            'date': transaction.date,
            'nameOrig': transaction.nameOrig,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': newbalanceOrig,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
            'ac_number': transaction.ac_number,
            'ifsc_code': transaction.ifsc_code,
            'transaction_type': transaction.transaction_type,
            'is_fraud': is_fraud,
            'isFlaggedFraud': transaction.isFlaggedFraud,
            'user_id': transaction.user_id  # Include user_id in the response
        }, status=status.HTTP_201_CREATED)

    return Response({'status': 'ok', 'message': 'transaction created successfully', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_transactions(request, user_id):
    # Filter transactions by user_id
    transactions = Transaction.objects.filter(user_id=user_id)

    # Serialize the transaction data
    serializer = TransactionSerializer(transactions, many=True)

    return Response({
        'status': 'ok',
        'message':'transaction history',
        'data': serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
def transaction_detail(request, user_id, transaction_id):
    try:
        # Retrieve the specific transaction by ID and user_id
        transaction = Transaction.objects.get(id=transaction_id, user_id=user_id)
        serializer = TransactionSerializer(transaction)
        
        return Response({
            'status': 'ok',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Transaction.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)