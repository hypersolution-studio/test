# 🚀 Guia Rápido - WhatsApp Bot para Imobiliárias

## Início Rápido em 5 Minutos

### 1️⃣ Subir o Ambiente com Docker

```bash
# Clonar ou navegar até o diretório do projeto
cd /caminho/do/projeto

# Copiar arquivo de configuração
cp .env.example .env

# Editar variáveis de ambiente (opcional)
nano .env

# Iniciar todos os serviços
docker-compose up -d

# Verificar se tudo está rodando
docker-compose ps
```

### 2️⃣ Acessar o n8n

1. Abra o navegador em: **http://localhost:5678**
2. Login:
   - Usuário: `admin`
   - Senha: `admin123`

### 3️⃣ Importar o Workflow

1. No n8n, clique em **"Workflows"** → **"Import from File"**
2. Selecione o arquivo: `whatsapp-imobiliaria-flow.json`
3. Clique em **"Import"**
4. O workflow estará pronto para uso!

### 4️⃣ Testar a API de Imóveis

```bash
# Testar se a API está funcionando
curl http://localhost:5000/health

# Buscar imóveis
curl "http://localhost:5000/buscar?tipo_negocio=aluguel&faixa_preco=1500_3000&dormitorios=2&tipo_imovel=apartamento&localizacao=Centro"
```

---

## 📱 Configurar WhatsApp

### Opção A: WhatsApp Business API Oficial

1. Criar conta no [Meta for Developers](https://developers.facebook.com/)
2. Configurar WhatsApp Business API
3. Obter credenciais (Token, Phone Number ID)
4. No n8n, configurar credenciais do WhatsApp nos nós

### Opção B: Evolution API (Recomendado para testes)

```bash
# Adicionar Evolution API ao docker-compose.yml
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  atendai/evolution-api:latest

# Acessar: http://localhost:8080
```

### Opção C: Baileys (Alternativa gratuita)

Instalar e configurar Baileys localmente ou via Docker.

---

## 🔧 Configurações Importantes

### Editar URLs da API

No workflow do n8n, procure por estes nós e atualize as URLs:

1. **"Buscar Imóveis no Estoque"**
   ```
   URL: http://api-imoveis:5000/buscar
   ```

2. **"Salvar Lead no CRM"**
   ```
   URL: http://api-imoveis:5000/leads
   ```

### Webhook do WhatsApp

Configure o webhook no seu provedor de WhatsApp para apontar para:

```
http://seu-dominio.com:5678/webhook/webhook-whatsapp
```

Ou use **ngrok** para testes locais:

```bash
ngrok http 5678

# Copie a URL gerada e configure no WhatsApp
https://xxxx-xx-xxx-xxx-xxx.ngrok.io/webhook/webhook-whatsapp
```

---

## 📊 Estrutura dos Arquivos

```
├── whatsapp-imobiliaria-flow.json   # Workflow principal do n8n
├── api_imoveis_exemplo.py           # API de busca de imóveis (Python)
├── exemplo-api-imoveis.json         # Documentação da API
├── README-WHATSAPP-FLOW.md          # Documentação completa
├── GUIA-RAPIDO.md                   # Este arquivo
├── requirements.txt                  # Dependências Python
├── docker-compose.yml               # Orquestração dos serviços
├── Dockerfile.api                   # Imagem Docker da API
└── .env.example                     # Variáveis de ambiente
```

---

## 🧪 Testar o Fluxo Completo

### 1. Enviar mensagem de teste

Se estiver usando Evolution API ou similar:

```bash
curl -X POST http://localhost:8080/message/sendText \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Olá"
  }'
```

### 2. Fluxo esperado

```
1. Bot: Olá! Bem-vindo... Aluguel (1) ou Compra (2)?
   Cliente: 1

2. Bot: Qual seu orçamento? [opções]
   Cliente: 6

3. Bot: Quantos dormitórios? [opções]
   Cliente: 2

4. Bot: Tipo de imóvel? [opções]
   Cliente: 1

5. Bot: Sala integrada ou separada? [opções]
   Cliente: 1

6. Bot: Quantas vagas de garagem? [opções]
   Cliente: 1

7. Bot: Qual região preferida?
   Cliente: Centro

8. Bot: 🎉 Encontrei 3 imóveis! [envia detalhes]
```

---

## 🛠️ Comandos Úteis

### Docker

```bash
# Ver logs da API
docker-compose logs -f api-imoveis

# Ver logs do n8n
docker-compose logs -f n8n

# Reiniciar um serviço
docker-compose restart api-imoveis

# Parar tudo
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### Executar API sem Docker

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API
python api_imoveis_exemplo.py

# Ou com gunicorn (produção)
gunicorn --bind 0.0.0.0:5000 api_imoveis_exemplo:app
```

---

## 📈 Adicionar Imóveis ao Banco

### Método 1: Editar o arquivo Python

Abra `api_imoveis_exemplo.py` e adicione imóveis ao array `IMOVEIS_DB`:

```python
IMOVEIS_DB.append({
    "id": 1006,
    "titulo": "Seu Imóvel Aqui",
    "tipo_negocio": "aluguel",
    # ... resto dos campos
})
```

### Método 2: Usar MongoDB

1. Conectar ao MongoDB:
   ```bash
   docker exec -it mongodb-imobiliaria mongosh -u admin -p admin123
   ```

2. Inserir imóvel:
   ```javascript
   use imobiliaria
   db.imoveis.insertOne({
     "titulo": "Novo Imóvel",
     "tipo_negocio": "aluguel",
     // ...
   })
   ```

---

## 🔐 Segurança para Produção

Antes de colocar em produção, altere:

1. ✅ Senhas do n8n (`.env`)
2. ✅ Senhas do MongoDB
3. ✅ Usar HTTPS (certificado SSL)
4. ✅ Configurar firewall
5. ✅ Adicionar autenticação na API
6. ✅ Rate limiting
7. ✅ Backup automático do banco

---

## 💡 Próximos Passos

- [ ] Conectar com WhatsApp real
- [ ] Integrar com seu banco de dados de imóveis
- [ ] Conectar com seu CRM
- [ ] Adicionar fotos dos imóveis
- [ ] Implementar agendamento de visitas
- [ ] Criar dashboard de métricas
- [ ] Treinar equipe para atendimento humano quando necessário

---

## 🆘 Problemas Comuns

### n8n não inicia
- Verificar se a porta 5678 está livre
- Checar logs: `docker-compose logs n8n`

### API não responde
- Verificar se a porta 5000 está livre
- Testar: `curl http://localhost:5000/health`

### WhatsApp não recebe mensagens
- Verificar configuração do webhook
- Verificar credenciais do WhatsApp
- Checar logs do n8n

### Imóveis não aparecem
- Verificar filtros da busca
- Conferir dados no `IMOVEIS_DB`
- Testar API diretamente com curl

---

## 📚 Recursos

- [Documentação n8n](https://docs.n8n.io)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Evolution API](https://evolution-api.com)
- [Flask Documentation](https://flask.palletsprojects.com)

---

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação completa em `README-WHATSAPP-FLOW.md`
2. Revise o arquivo `exemplo-api-imoveis.json`
3. Consulte os logs dos containers

---

**Desenvolvido com ❤️ para transformar o atendimento de imobiliárias**
