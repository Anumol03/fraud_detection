from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myapp.serializers import *
from myapp.models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import load_model

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
def bank_account_detail(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
    except BankAccount.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BankSerializer(bank_account)
        return Response({"status":"ok","message":"account details retrived successfully","data":serializer.data})
    


@api_view(['POST'])
def create_transaction(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        # Extract the provided amount
        amount = serializer.validated_data['amount']
        
        # Assuming 'nameOrig' identifies the customer, and using it to fetch previous transaction balances
        nameOrig = serializer.validated_data['nameOrig']

        # Fetch the last transaction of the customer, if available
        last_transaction = Transaction.objects.filter(nameOrig=nameOrig).order_by('-id').first()

        if last_transaction:
            oldbalanceOrg = last_transaction.newbalanceOrig
            oldbalanceDest = last_transaction.newbalanceDest
        else:
            # Default values for first transaction (e.g., 0 or some other initial values)
            oldbalanceOrg = 200000.00  # Initial balance of 2 lakhs
            oldbalanceDest = 200000.00  # Initial balance of 2 lakhs

        # Calculate new balances after the transaction
        newbalanceOrig = oldbalanceOrg - amount
        newbalanceDest = oldbalanceDest + amount

        # Calculate total balance after transaction (if needed globally)
        total_balance_after_transaction = newbalanceOrig + newbalanceDest

        # Load the logistic regression model
        model = load_model()

        # Prepare the features for fraud detection
        features = [
            amount,
            oldbalanceOrg,
            newbalanceOrig,
            oldbalanceDest,
            newbalanceDest
        ]

        # Predict whether the transaction is fraudulent
        prediction = model.predict([features])
        is_fraud = bool(prediction[0])

        # Save the transaction with the calculated fields
        transaction = serializer.save(
            oldbalanceOrg=oldbalanceOrg,
            newbalanceOrig=newbalanceOrig,
            oldbalanceDest=oldbalanceDest,
            newbalanceDest=newbalanceDest,
            total_balance=total_balance_after_transaction,
            is_fraud=is_fraud,
            isFlaggedFraud=0.0  # Set default value for isFlaggedFraud
        )

        return Response({
            'transaction_id': transaction.id,
            'amount': amount,
            'nameOrig': nameOrig,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': newbalanceOrig,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
            'ac_name': transaction.ac_name,
            'ifsc_code': transaction.ifsc_code,
            'recipient_name': transaction.recipient_name,
            'transaction_type': transaction.transaction_type,
            'total_balance': total_balance_after_transaction,
            'is_fraud': is_fraud,
            'isFlaggedFraud': transaction.isFlaggedFraud
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
