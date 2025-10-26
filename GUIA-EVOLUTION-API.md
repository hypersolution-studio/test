# Guia Completo: Evolution API + WhatsApp Business + n8n

## Índice
1. [O que é Evolution API](#o-que-é-evolution-api)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação da Evolution API](#instalação-da-evolution-api)
4. [Conectar WhatsApp Business](#conectar-whatsapp-business)
5. [Integração com n8n](#integração-com-n8n)
6. [Testar Tudo Funcionando](#testar-tudo-funcionando)
7. [Troubleshooting](#troubleshooting)

---

## O que é Evolution API

**Evolution API** é uma API REST completa para integração com WhatsApp, que permite:
- ✅ Conectar múltiplas contas WhatsApp
- ✅ Enviar e receber mensagens
- ✅ Enviar mídias (imagens, vídeos, documentos)
- ✅ Gerenciar grupos
- ✅ Webhooks automáticos
- ✅ Interface web para gerenciamento

**Vantagem**: Não precisa da API oficial do Meta (WhatsApp Business API), funciona com qualquer WhatsApp.

---

## Pré-requisitos

Antes de começar, você precisa de:

- [ ] Docker e Docker Compose instalados
- [ ] Porta 8080 livre (para Evolution API)
- [ ] Porta 5678 livre (para n8n)
- [ ] Celular com WhatsApp instalado (será sua linha business)
- [ ] Conexão com internet estável

---

## Instalação da Evolution API

### Opção 1: Adicionar ao Docker Compose Existente (Recomendado)

Vamos adicionar a Evolution API ao seu `docker-compose.yml`:

```yaml
# Adicione este serviço ao seu docker-compose.yml existente
  evolution-api:
    image: atendai/evolution-api:v2.1.1
    container_name: evolution-api
    restart: always
    ports:
      - "8080:8080"
    environment:
      # Configurações básicas
      - SERVER_URL=http://localhost:8080
      - AUTHENTICATION_API_KEY=sua-chave-secreta-aqui-12345

      # Configurações de armazenamento
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution
      - DATABASE_SAVE_DATA_INSTANCE=true
      - DATABASE_SAVE_DATA_NEW_MESSAGE=true
      - DATABASE_SAVE_MESSAGE_UPDATE=true
      - DATABASE_SAVE_DATA_CONTACTS=true
      - DATABASE_SAVE_DATA_CHATS=true

      # Redis para cache
      - CACHE_REDIS_ENABLED=true
      - CACHE_REDIS_URI=redis://redis:6379/1
      - CACHE_REDIS_PREFIX_KEY=evolution

      # Configurações de Webhook
      - WEBHOOK_GLOBAL_ENABLED=true
      - WEBHOOK_GLOBAL_URL=http://n8n:5678/webhook/whatsapp-webhook
      - WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS=true

      # Configurações de QR Code
      - QRCODE_LIMIT=30
      - QRCODE_COLOR=#175197

      # Configurações de logs
      - LOG_LEVEL=ERROR,WARN,DEBUG,INFO,LOG,VERBOSE,DARK,WEBHOOKS
      - LOG_COLOR=true

      # Configurações de instância
      - DEL_INSTANCE=false

    volumes:
      - evolution_data:/evolution/instances
      - evolution_store:/evolution/store
    networks:
      - imobiliaria-network
    depends_on:
      - postgres
      - redis

  # Banco de dados PostgreSQL para Evolution API
  postgres:
    image: postgres:15-alpine
    container_name: postgres-evolution
    restart: always
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=evolution
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - imobiliaria-network

# Adicione estes volumes no final do arquivo
volumes:
  evolution_data:
  evolution_store:
  postgres_data:
```

### Opção 2: Instalação Standalone (Simples e Rápida)

Se quiser testar primeiro sem integrar ao docker-compose:

```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=minha-chave-secreta-123 \
  -e SERVER_URL=http://localhost:8080 \
  atendai/evolution-api:latest
```

---

## Conectar WhatsApp Business

### Passo 1: Subir a Evolution API

```bash
# Se estiver usando docker-compose completo
docker-compose up -d evolution-api postgres

# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs -f evolution-api
```

Aguarde até ver a mensagem: **"Evolution API is ready"**

### Passo 2: Acessar a Interface da Evolution API

Abra no navegador:
```
http://localhost:8080
```

**Você verá a documentação interativa da API (Swagger)**

### Passo 3: Criar uma Instância do WhatsApp

Vamos criar uma instância usando a API. Você pode fazer via:

#### Via cURL:

```bash
curl -X POST 'http://localhost:8080/instance/create' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{
    "instanceName": "imobiliaria-bot",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

#### Via Postman/Insomnia:

- **Método**: POST
- **URL**: `http://localhost:8080/instance/create`
- **Headers**:
  - `Content-Type`: `application/json`
  - `apikey`: `sua-chave-secreta-aqui-12345`
- **Body (JSON)**:
```json
{
  "instanceName": "imobiliaria-bot",
  "qrcode": true,
  "integration": "WHATSAPP-BAILEYS"
}
```

**Resposta esperada**:
```json
{
  "instance": {
    "instanceName": "imobiliaria-bot",
    "status": "created"
  },
  "hash": {
    "apikey": "sua-instancia-key-aqui"
  }
}
```

⚠️ **IMPORTANTE**: Guarde o `apikey` retornado, você vai usar nas próximas etapas!

### Passo 4: Conectar seu WhatsApp

Agora vamos gerar o QR Code para conectar:

```bash
curl -X GET 'http://localhost:8080/instance/connect/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

**Resposta**: Você receberá um QR Code em base64 ou um link para visualizar.

#### Visualizar QR Code:

**Opção A - Via Navegador**:
```
http://localhost:8080/instance/qrcode/imobiliaria-bot?apikey=sua-chave-secreta-aqui-12345
```

**Opção B - Via Terminal** (se tiver qrencode instalado):
```bash
# Instalar qrencode
sudo apt-get install qrencode  # Linux
brew install qrencode           # Mac

# Gerar QR Code no terminal
curl -s 'http://localhost:8080/instance/qrcode/imobiliaria-bot?apikey=sua-chave-secreta-aqui-12345' | qrencode -t UTF8
```

### Passo 5: Escanear QR Code com seu WhatsApp

1. **Abra o WhatsApp no seu celular**
2. **Android**: Menu (⋮) → Aparelhos conectados → Conectar um aparelho
3. **iPhone**: Configurações → Aparelhos conectados → Conectar um aparelho
4. **Escaneie o QR Code** que apareceu na tela
5. **Aguarde a conexão** (15-30 segundos)

### Passo 6: Verificar Conexão

```bash
curl -X GET 'http://localhost:8080/instance/connectionState/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

**Resposta esperada** (conectado):
```json
{
  "instance": {
    "instanceName": "imobiliaria-bot",
    "state": "open"
  }
}
```

✅ **Pronto! Seu WhatsApp está conectado à Evolution API!**

---

## Integração com n8n

Agora vamos conectar a Evolution API ao workflow do n8n que criamos.

### Passo 1: Configurar Webhook na Evolution API

A Evolution API enviará todas as mensagens recebidas para o n8n via webhook.

```bash
curl -X POST 'http://localhost:8080/webhook/set/imobiliaria-bot' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{
    "enabled": true,
    "url": "http://n8n:5678/webhook/whatsapp-webhook",
    "webhookByEvents": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "SEND_MESSAGE"
    ]
  }'
```

**Se estiver rodando localmente (fora do Docker)**:
```json
{
  "enabled": true,
  "url": "http://localhost:5678/webhook/whatsapp-webhook",
  "webhookByEvents": true,
  "events": ["MESSAGES_UPSERT"]
}
```

### Passo 2: Atualizar Workflow do n8n

Precisamos adaptar o workflow para o formato de dados da Evolution API.

#### Criar Novo Workflow: "Evolution API → n8n"

Arquivo: `whatsapp-evolution-n8n.json`

Vou criar este arquivo para você com a integração completa.

### Passo 3: Criar Nó de Resposta para Evolution API

No n8n, precisamos adicionar um nó que **envie mensagens de volta** via Evolution API.

**HTTP Request Node** com estas configurações:
- **Method**: POST
- **URL**: `http://evolution-api:8080/message/sendText/imobiliaria-bot`
- **Headers**:
  - `apikey`: `sua-chave-secreta-aqui-12345`
  - `Content-Type`: `application/json`
- **Body**:
```json
{
  "number": "{{ $json.telefone }}",
  "text": "{{ $json.resposta_final }}"
}
```

---

## Testar Tudo Funcionando

### Teste 1: Enviar Mensagem Manualmente via API

```bash
curl -X POST 'http://localhost:8080/message/sendText/imobiliaria-bot' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{
    "number": "5511999999999",
    "text": "Olá! Este é um teste da Evolution API."
  }'
```

**Você deve receber a mensagem no seu WhatsApp!**

### Teste 2: Enviar Mensagem e Testar Resposta Automática

1. **Do seu celular**, envie uma mensagem para o número conectado
2. **Digite**: "Olá"
3. **Aguarde 2-5 segundos**
4. **Deve receber**: "Olá! 👋 Bem-vindo à nossa imobiliária..."

### Teste 3: Fluxo Completo

Simule uma conversa completa:

1. Você: "Oi"
2. Bot: "Bem-vindo... Aluguel (1) ou Compra (2)?"
3. Você: "1"
4. Bot: "Qual sua faixa de orçamento..."
5. Você: "2"
6. Bot: "Quantos dormitórios..."
... e assim por diante

---

## Troubleshooting

### Problema: QR Code não aparece

**Solução**:
```bash
# Verificar logs
docker logs evolution-api -f

# Recriar instância
curl -X DELETE 'http://localhost:8080/instance/delete/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'

# Criar novamente
curl -X POST 'http://localhost:8080/instance/create' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{"instanceName":"imobiliaria-bot","qrcode":true}'
```

### Problema: WhatsApp desconecta

**Solução**:
- Não feche o WhatsApp do celular por muito tempo
- Mantenha o celular com internet
- Configure `DEL_INSTANCE=false` no docker-compose
- Use Redis para persistência de sessão

### Problema: n8n não recebe mensagens

**Solução**:
```bash
# Verificar webhook configurado
curl -X GET 'http://localhost:8080/webhook/find/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'

# Testar webhook manualmente
curl -X POST 'http://localhost:5678/webhook/whatsapp-webhook' \
  -H 'Content-Type: application/json' \
  -d '{
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net"
    },
    "message": {
      "conversation": "teste"
    }
  }'
```

### Problema: Mensagens não são enviadas

**Solução**:
- Verificar se apikey está correta
- Verificar formato do número (incluir DDI+DDD)
- Exemplo: Brasil → `5511999999999`
- Verificar logs do n8n: `docker logs n8n-imobiliaria -f`

### Problema: Erro 401 Unauthorized

**Solução**:
- Verificar se o header `apikey` está sendo enviado
- Confirmar se a chave está correta
- Verificar variável de ambiente `AUTHENTICATION_API_KEY`

---

## Comandos Úteis

### Listar Instâncias
```bash
curl -X GET 'http://localhost:8080/instance/fetchInstances' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

### Ver Status da Instância
```bash
curl -X GET 'http://localhost:8080/instance/connectionState/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

### Desconectar WhatsApp
```bash
curl -X DELETE 'http://localhost:8080/instance/logout/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

### Deletar Instância
```bash
curl -X DELETE 'http://localhost:8080/instance/delete/imobiliaria-bot' \
  -H 'apikey: sua-chave-secreta-aqui-12345'
```

### Enviar Mensagem com Mídia
```bash
# Enviar imagem
curl -X POST 'http://localhost:8080/message/sendMedia/imobiliaria-bot' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{
    "number": "5511999999999",
    "mediatype": "image",
    "media": "https://exemplo.com/imagem.jpg",
    "caption": "Confira este imóvel!"
  }'
```

### Enviar Botões (Lista de Opções)
```bash
curl -X POST 'http://localhost:8080/message/sendList/imobiliaria-bot' \
  -H 'Content-Type: application/json' \
  -H 'apikey: sua-chave-secreta-aqui-12345' \
  -d '{
    "number": "5511999999999",
    "title": "Escolha uma opção",
    "description": "Selecione o tipo de negócio",
    "buttonText": "Ver opções",
    "sections": [
      {
        "title": "Tipo de Negócio",
        "rows": [
          {"title": "Aluguel", "description": "Imóveis para alugar"},
          {"title": "Compra", "description": "Imóveis para comprar"}
        ]
      }
    ]
  }'
```

---

## Próximos Passos

Após tudo funcionando:

1. ✅ Personalizar mensagens do bot
2. ✅ Adicionar mais imóveis no banco de dados
3. ✅ Configurar envio de imagens dos imóveis
4. ✅ Implementar botões interativos
5. ✅ Adicionar agendamento de visitas
6. ✅ Configurar múltiplos atendentes
7. ✅ Criar dashboard de métricas
8. ✅ Configurar backup automático

---

## Segurança e Boas Práticas

### Para Produção:

1. **Use HTTPS**: Configure certificado SSL (Let's Encrypt)
2. **Firewall**: Restrinja acesso às portas 8080 e 5678
3. **API Key Forte**: Use chaves longas e aleatórias
4. **Backup**: Configure backup do PostgreSQL
5. **Logs**: Configure rotação de logs
6. **Monitoring**: Use Prometheus + Grafana
7. **Rate Limiting**: Limite requisições por minuto

### Exemplo de API Key Segura:
```bash
# Gerar chave aleatória
openssl rand -base64 32
```

---

## Recursos Adicionais

- **Documentação Evolution API**: https://doc.evolution-api.com/
- **GitHub**: https://github.com/EvolutionAPI/evolution-api
- **Comunidade Discord**: https://evolution-api.com/discord
- **Exemplos de Código**: https://github.com/EvolutionAPI/evolution-api-examples

---

## Checklist Final

- [ ] Evolution API rodando
- [ ] PostgreSQL configurado
- [ ] Redis configurado (opcional mas recomendado)
- [ ] Instância WhatsApp criada
- [ ] QR Code escaneado
- [ ] Conexão verificada (state: open)
- [ ] Webhook configurado apontando para n8n
- [ ] Workflow n8n importado e ativo
- [ ] Teste de envio manual funcionou
- [ ] Teste de resposta automática funcionou
- [ ] Fluxo completo testado

---

**Parabéns! 🎉 Seu bot de WhatsApp para imobiliária está pronto e funcionando!**
