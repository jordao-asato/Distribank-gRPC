# Projeto: Sistema de Gerenciamento Bancário com gRPC

## Tecnologias
- Python 3
- gRPC
- Redis
- Protobuf

# Criar venv
python3 -m venv venv

# Ativar venv (no Linux/WSL/Mac)
source venv/bin/activate

## Como rodar
0. Instalar os requerimentos: `pip install -r requirements.txt`
1. Subir o Redis: `redis-server`
2. Rodar o servidor: `python3 server/server.py`
3. Rodar o cliente para testar: `python3 client/test_client.py`

## Funcionalidades
- Criar contas bancárias
- Consultar saldo
- Depositar fundos
- Sacar fundos
- Aplicar juros

# test_client
- está ali pra testar valores diretamente no código
- sem o menu interativo

## OBS
- Para deletar um ID: `redis-cli DEL [ID]` (sem os colchetes)

## Autor
Jordão Asato
