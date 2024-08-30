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
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([AllowAny])
def create_custom_user(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"ok","message":"account created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_custom_users(request):
    users = CustomUser.objects.all()  
    serializer = CustomUserSerializer(users, many=True, context={'request': request}) 
    return Response({"status":"ok","message":"list users successfully","data":serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_custom_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)  
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CustomUserSerializer(user, context={'request': request})  
    return Response({"status":"ok","message":"user retrieved successfully","data":serializer.data}, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def delete_custom_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response({"status": "ok", "message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
@permission_classes([AllowAny])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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

        # Define oldbalanceOrg choices as tuples
        oldbalanceOrg_choices = (
            (Decimal('170136.0'), 'Option 1'),
            (Decimal('21249.0'), 'Option 2'),
            (Decimal('181.0'), 'Option 3'),
            (Decimal('23647.0'), 'Option 4'),
            (Decimal('106071.0'), 'Option 5')
        )
        
        # Randomly select index from the tuple and unpack
        index_org = random.randint(0, len(oldbalanceOrg_choices) - 1)
        oldbalanceOrg, _ = oldbalanceOrg_choices[index_org]  # Unpacking the choice

        # Define oldbalanceDest choices as tuples
        oldbalanceDest_choices = (
            (Decimal('0.0'), 'Option A'),
            (Decimal('21182.0'), 'Option B'),
            (Decimal('173527.1'), 'Option C'),
            (Decimal('110696.18'), 'Option D'),
            (Decimal('0.0'), 'Option E')
        )
        
        # Randomly select index from the tuple and unpack
        index_dest = random.randint(0, len(oldbalanceDest_choices) - 1)
        oldbalanceDest, _ = oldbalanceDest_choices[index_dest]  # Unpacking the choice

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

        # If the transaction is marked as fraudulent, send an email
        if is_fraud:
            user_email = request.user.email  # Now safe to access
            send_mail(
                'Fraudulent Transaction Warning',
                'Dear user,\n\nYour recent transaction attempt has been flagged as potentially fraudulent. Please check your account for unauthorized activities.\n\nBest regards,\nYour Finance Team',
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )
            return Response({
                'status': 'error',
                'message': 'Transaction not possible due to fraud detection. A warning email has been sent.',
            }, status=status.HTTP_403_FORBIDDEN)  # Return a forbidden status

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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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



ADVICE_LIST = [
    {"id": 1, "category": "security", "text": "Always use two-factor authentication."},
    {"id": 2, "category": "transaction", "text": "Double-check the recipient's details before sending funds."},
    {"id": 3, "category": "privacy", "text": "Avoid using public Wi-Fi for sensitive transactions."},
    {"id": 4, "category": "awareness", "text": "Be cautious of phishing emails."},
    {"id": 5, "category": "security", "text": "Keep your software updated to protect against vulnerabilities."},
    {"id": 6, "category": "finance", "text": "Create a budget and stick to it."},
    {"id": 7, "category": "investment", "text": "Diversify your investments to reduce risk."},
    {"id": 8, "category": "planning", "text": "Always have an emergency fund for unexpected expenses."},
    {"id": 9, "category": "spending", "text": "Limit impulse purchases to stay within budget."},
    {"id": 10, "category": "savings", "text": "Aim to save at least 20% of your income."},
    {"id": 11, "category": "education", "text": "Keep learning about personal finance."},
    {"id": 12, "category": "goal-setting", "text": "Set clear financial goals to stay focused."},
    {"id": 13, "category": "debt", "text": "Pay off high-interest debt as soon as possible."},
    {"id": 14, "category": "shopping", "text": "Use a shopping list to avoid unnecessary purchases."},
    {"id": 15, "category": "financial literacy", "text": "Read books about personal finance and investing."},
]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def random_advice_view(request):
    random_advice = random.choice(ADVICE_LIST)  
    return Response(random_advice)


@api_view(['POST'])
def password_reset_view(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # No arguments passed here
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)