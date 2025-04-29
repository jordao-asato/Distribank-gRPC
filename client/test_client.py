import grpc

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generated import bank_pb2, bank_pb2_grpc

def get_balance(stub, account_id):
    try:
        response = stub.GetBalance(bank_pb2.BalanceResponse(account_id=account_id))
        return response.balance
    except grpc.RpcError as e:
        print(f"Erro: {e.code()} - {e.details()}")
        return None

def deposit(stub, account_id, amount):
    try:
        response = stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=amount))
        return response.message
    except grpc.RpcError as e:
        print(f"Erro: {e.code()} - {e.details()}")
        return None
    
def withdraw(stub, account_id, amount):
    try:
        response = stub.Withdraw(bank_pb2.WithdrawRequest(
            account_id=account_id,
            amount=amount
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code()} - {e.details()}")

def calculate_interest(stub, account_id, annual_interest_rate):
    try:
        response = stub.CalculateInterest(bank_pb2.InterestRequest(
            account_id=account_id,
            annual_interest_rate=annual_interest_rate
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code()} - {e.details()}")


def run():
    # Conectando no servidor
    channel = grpc.insecure_channel('localhost:50051')
    stub = bank_pb2_grpc.BankServiceStub(channel)
    
    try:
        response = stub.CreateAccount(bank_pb2.AccountRequest(
            account_id="1234",
            account_type="poupanca"
        ))
        
        print("Resposta do servidor:", response.message)

        # Consultar saldo
        balance = get_balance(stub, '1234')
        if balance is not None:
            print(f"Saldo da conta 1234: R$ {balance:.2f}")

        # Fazer depósito
        message = deposit(stub, '1234', 500.0)
        if message:
            print(message)
        
        # Consultar saldo após depósito
        balance = get_balance(stub, '1234')
        if balance is not None:
            print(f"Saldo após depósito da conta 1234: R$ {balance:.2f}")

        withdraw(stub, "1234", 100.0)

        # Calcula juros normalmente
        calculate_interest(stub, "1234", 5.0)  # 5% de juros

        # Consulta saldo depois dos juros
        get_balance(stub, "1234")

        # Testa juros com valor inválido (negativo)
        calculate_interest(stub, "1234", -2.0)

        # Testa em conta inexistente
        calculate_interest(stub, "999", 5.0)

    except grpc.RpcError as e:
        print(f"Erro ao chamar o servidor: {e.code()} - {e.details()}")

if __name__ == '__main__':
    run()
