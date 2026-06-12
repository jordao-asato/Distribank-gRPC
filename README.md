# DistriBank — Sistema Bancário Distribuído com gRPC

> Serviço bancário distribuído implementado com gRPC, Protocol Buffers e Redis, com tratamento de concorrência para operações financeiras simultâneas.

---

## 📋 Sobre o Projeto

O **DistriBank** é um serviço de back-end que simula as operações essenciais de um sistema bancário (criação de contas, consultas de saldo, depósitos, saques e cálculo de juros) usando uma arquitetura **cliente-servidor distribuída** baseada em **gRPC**. A persistência dos dados é feita em **Redis**, e o acesso concorrente ao mesmo recurso (saldo de uma conta) é protegido por **locks distribuídos**, evitando condições de corrida (*race conditions*) em operações críticas.

Este projeto explora conceitos centrais de Sistemas Distribuídos: comunicação remota via RPC (Remote Procedure Call), serialização eficiente com Protocol Buffers, controle de concorrência e consistência de dados em ambiente compartilhado.

---

## 🚀 Funcionalidades

- 🏦 **Criação de contas** — cadastro de contas correntes ou poupança
- 💰 **Consulta de saldo** — leitura do saldo atual de uma conta
- ⬆️ **Depósito** — adição de fundos com proteção via lock distribuído
- ⬇️ **Saque** — retirada de fundos com validação de saldo disponível
- 📈 **Cálculo de juros** — aplicação de taxa de juros anual sobre o saldo
- ⚠️ **Tratamento de erros** — uso de status codes padronizados do gRPC (`NOT_FOUND`, `ALREADY_EXISTS`, `INVALID_ARGUMENT`, `FAILED_PRECONDITION`)

---

## 🏗️ Arquitetura

```
┌────────────────┐       gRPC (porta 50051)        ┌──────────────────┐
│  Client (CLI)   │ ─────────────────────────────►  │   gRPC Server     │
│  client.py      │ ◄─────────────────────────────  │   server.py       │
└────────────────┘                                  └──────────┬────────┘
                                                                 │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │    Redis     │
                                                          │ (porta 6379) │
                                                          └─────────────┘
```

A comunicação entre cliente e servidor é definida por um **contrato Protobuf** (`bank.proto`), compilado em stubs Python (`bank_pb2.py` e `bank_pb2_grpc.py`). O servidor expõe um serviço `BankService` com 5 RPCs, executado em um pool de threads (`ThreadPoolExecutor`), permitindo atender múltiplas requisições simultâneas.

---

## 📁 Estrutura do Projeto

```
.
├── proto/
│   └── bank.proto          # Definição do contrato gRPC (serviços e mensagens)
├── generated/
│   ├── bank_pb2.py          # Código gerado: mensagens Protobuf
│   └── bank_pb2_grpc.py      # Código gerado: stubs e servicers gRPC
├── server/
│   └── server.py             # Implementação do servidor gRPC + lógica de negócio
├── client/
│   ├── client.py              # Cliente CLI interativo (menu)
│   └── test_client.py         # Script de testes automatizados (sem menu)
└── requirements.txt           # Dependências do projeto
```

---

## 🔌 Contrato gRPC (bank.proto)

| RPC | Requisição | Resposta | Descrição |
|---|---|---|---|
| `CreateAccount` | `AccountRequest` | `AccountResponse` | Cria uma nova conta (corrente/poupança) |
| `GetBalance` | `AccountRequest` | `BalanceResponse` | Retorna o saldo atual da conta |
| `Deposit` | `DepositRequest` | `TransactionResponse` | Deposita um valor na conta |
| `Withdraw` | `WithdrawRequest` | `TransactionResponse` | Retira um valor da conta |
| `CalculateInterest` | `InterestRequest` | `TransactionResponse` | Aplica juros sobre o saldo atual |

---

## 🔒 Controle de Concorrência

A operação de **depósito** demonstra o tratamento de concorrência exigido em sistemas distribuídos: antes de ler e atualizar o saldo, o servidor adquire um **lock distribuído no Redis** (`redis_client.lock`) específico para a conta (`lock:{account_id}`), com timeout de 5 segundos. Isso garante que múltiplas requisições simultâneas à mesma conta sejam serializadas, prevenindo *race conditions* na leitura-modificação-escrita do saldo.

---

## 🛠️ Tecnologias

- **Python 3.12**
- **gRPC** (`grpcio`, `grpcio-tools`) — comunicação RPC
- **Protocol Buffers** — serialização e definição de contrato
- **Redis** — armazenamento de contas e locks distribuídos

---

## ⚙️ Como Executar

### 1. Pré-requisitos

- Python 3.10+
- Redis instalado (ou via Docker: `docker run -p 6379:6379 redis`)

### 2. Configurar o ambiente

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Subir o Redis

```bash
redis-server
```

### 4. Rodar o servidor

```bash
python3 server/server.py
```

O servidor ficará disponível em `localhost:50051`.

### 5. Rodar o cliente

**Modo interativo** (menu com criação de conta, depósito, saque, etc.):
```bash
python3 client/client.py
```

**Modo de teste automatizado** (executa uma sequência de operações pré-definidas no código):
```bash
python3 client/test_client.py
```

---

## 🔧 Regenerando os Stubs gRPC (opcional)

Caso o arquivo `bank.proto` seja modificado, os stubs podem ser regerados com:

```bash
python -m grpc_tools.protoc -I proto --python_out=generated --grpc_python_out=generated proto/bank.proto
```

---

## 🗑️ Manutenção (Redis)

Para remover uma conta do banco de dados durante testes:

```bash
redis-cli DEL <account_id>
```

---

## 👤 Autor

**Jordão Asato**
