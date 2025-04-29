import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generated import bank_pb2, bank_pb2_grpc

def create_account(stub):
    account_id = input("Digite o ID da nova conta: ")
    account_type = input("Digite o tipo de conta ('corrente' ou 'poupanca'): ")
    try:
        response = stub.CreateAccount(bank_pb2.AccountRequest(
            account_id=account_id,
            account_type=account_type
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code().name} - {e.details()}")

def get_balance(stub):
    account_id = input("Digite o ID da conta: ")
    try:
        response = stub.GetBalance(bank_pb2.AccountRequest(
            account_id=account_id
        ))
        print(f"Saldo: R$ {response.balance:.2f}")
    except grpc.RpcError as e:
        print(f"Erro: {e.code().name} - {e.details()}")

def deposit(stub):
    account_id = input("Digite o ID da conta: ")
    amount = float(input("Digite o valor do depósito: "))
    try:
        response = stub.Deposit(bank_pb2.DepositRequest(
            account_id=account_id,
            amount=amount
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code().name} - {e.details()}")

def withdraw(stub):
    account_id = input("Digite o ID da conta: ")
    amount = float(input("Digite o valor do saque: "))
    try:
        response = stub.Withdraw(bank_pb2.WithdrawRequest(
            account_id=account_id,
            amount=amount
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code().name} - {e.details()}")

def calculate_interest(stub):
    account_id = input("Digite o ID da conta: ")
    rate = float(input("Digite a taxa de juros anual (%): "))
    try:
        response = stub.CalculateInterest(bank_pb2.InterestRequest(
            account_id=account_id,
            annual_interest_rate=rate
        ))
        print(response.message)
    except grpc.RpcError as e:
        print(f"Erro: {e.code().name} - {e.details()}")

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bank_pb2_grpc.BankServiceStub(channel)

        while True:
            print("\n=== Banco Distribuído ===")
            print("1. Criar conta")
            print("2. Consultar saldo")
            print("3. Depositar")
            print("4. Sacar")
            print("5. Calcular juros")
            print("0. Sair")

            option = input("Escolha uma opção: ")

            if option == '1':
                create_account(stub)
            elif option == '2':
                get_balance(stub)
            elif option == '3':
                deposit(stub)
            elif option == '4':
                withdraw(stub)
            elif option == '5':
                calculate_interest(stub)
            elif option == '0':
                print("Saindo...")
                break
            else:
                print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main()
