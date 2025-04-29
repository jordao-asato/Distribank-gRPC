import grpc
from concurrent import futures
import redis
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from generated import bank_pb2, bank_pb2_grpc

class BankService(bank_pb2_grpc.BankServiceServicer):
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def CreateAccount(self, request, context):
        account_id = request.account_id
        account_type = request.account_type.lower()

        # Verifica se a conta já existe
        if self.redis_client.exists(account_id):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Conta já existe.")

        # Cria a conta no Redis
        account_data = {
            'account_id': account_id,
            'account_type': account_type,
            'balance': 0.0
        }

        self.redis_client.hset(account_id, mapping=account_data)

        return bank_pb2.AccountResponse(message=f"Conta {account_id} criada com sucesso!")
    
    def GetBalance(self, request, context):
        account_id = request.account_id

        # Verifica se a conta existe
        if not self.redis_client.exists(account_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "Conta não encontrada. Verifique o ID da conta.")

        balance = float(self.redis_client.hget(account_id, 'balance'))

        return bank_pb2.BalanceResponse(balance=balance)
    
    def Deposit(self, request, context):
        account_id = request.account_id
        amount = request.amount

        if amount <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "O valor da transação deve ser positivo.")

        if not self.redis_client.exists(account_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "Conta não encontrada. Verifique o ID da conta.")

        # (LOCK para tratar simultaneidade)
        lock_name = f"lock:{account_id}"
        with self.redis_client.lock(lock_name, blocking_timeout=5):
            balance = float(self.redis_client.hget(account_id, 'balance'))
            new_balance = balance + amount
            self.redis_client.hset(account_id, 'balance', new_balance)

        return bank_pb2.TransactionResponse(message=f"Depósito de R$ {amount:.2f} realizado com sucesso.")

    def Withdraw(self, request, context):
        account_id = request.account_id
        amount = request.amount

        if amount <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "O valor da transação deve ser positivo.")

        if not self.redis_client.exists(account_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "Conta não encontrada. Verifique o ID da conta.")

        account_data = self.redis_client.hgetall(account_id)
        current_balance = float(account_data[b'balance'].decode('utf-8'))

        if current_balance < amount:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Fundos insuficientes para o saque solicitado.")

        new_balance = current_balance - amount

        # Atualiza saldo
        self.redis_client.hset(account_id, 'balance', new_balance)

        return bank_pb2.AccountResponse(message=f"Saque de {amount} realizado com sucesso! Saldo atual: {new_balance}")

    def CalculateInterest(self, request, context):
        account_id = request.account_id
        annual_interest_rate = request.annual_interest_rate

        if annual_interest_rate <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "A taxa de juros anual deve ser um valor positivo.")

        if not self.redis_client.exists(account_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "Conta não encontrada. Verifique o ID da conta.")

        account_data = self.redis_client.hgetall(account_id)
        current_balance = float(account_data[b'balance'].decode('utf-8'))

        # Cálculo dos juros
        interest = current_balance * (annual_interest_rate / 100)
        new_balance = current_balance + interest

        # Atualiza saldo
        self.redis_client.hset(account_id, 'balance', new_balance)

        return bank_pb2.AccountResponse(
            message=f"Juros de {interest:.2f} aplicados. Novo saldo: {new_balance:.2f}"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Servidor gRPC rodando na porta 50051...')
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor ativo
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
