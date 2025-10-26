#!/bin/bash

# Scripts de Teste para Evolution API + WhatsApp + n8n
# =====================================================

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações (EDITE AQUI)
EVOLUTION_URL="http://localhost:8080"
API_KEY="sua-chave-secreta-aqui-12345"
INSTANCE_NAME="imobiliaria-bot"
NUMERO_TESTE="5511999999999"  # Seu número de WhatsApp para teste

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Scripts de Teste - Evolution API + n8n     ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo ""

# Função para aguardar
pause() {
    echo -e "${YELLOW}Pressione Enter para continuar...${NC}"
    read
}

# Menu principal
show_menu() {
    echo ""
    echo -e "${GREEN}=== MENU DE TESTES ===${NC}"
    echo ""
    echo "1) Verificar se Evolution API está rodando"
    echo "2) Criar instância do WhatsApp"
    echo "3) Gerar QR Code para conectar"
    echo "4) Verificar status da conexão"
    echo "5) Configurar webhook para n8n"
    echo "6) Enviar mensagem de teste"
    echo "7) Simular fluxo completo (via webhook)"
    echo "8) Listar todas as instâncias"
    echo "9) Ver logs da Evolution API"
    echo "10) Teste completo (end-to-end)"
    echo "0) Sair"
    echo ""
    echo -n "Escolha uma opção: "
    read option
}

# 1) Verificar se Evolution API está rodando
test_evolution_running() {
    echo -e "${BLUE}[1] Verificando Evolution API...${NC}"

    response=$(curl -s -o /dev/null -w "%{http_code}" "$EVOLUTION_URL")

    if [ "$response" = "200" ] || [ "$response" = "401" ]; then
        echo -e "${GREEN}✓ Evolution API está rodando!${NC}"
        echo "URL: $EVOLUTION_URL"
    else
        echo -e "${RED}✗ Evolution API não está acessível!${NC}"
        echo "Código HTTP: $response"
        echo ""
        echo "Execute: docker-compose up -d evolution-api"
    fi
}

# 2) Criar instância
create_instance() {
    echo -e "${BLUE}[2] Criando instância do WhatsApp...${NC}"

    response=$(curl -s -X POST "$EVOLUTION_URL/instance/create" \
        -H "Content-Type: application/json" \
        -H "apikey: $API_KEY" \
        -d "{
            \"instanceName\": \"$INSTANCE_NAME\",
            \"qrcode\": true,
            \"integration\": \"WHATSAPP-BAILEYS\"
        }")

    echo "$response" | jq '.'

    if echo "$response" | jq -e '.instance' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Instância criada com sucesso!${NC}"
        echo ""
        echo -e "${YELLOW}IMPORTANTE: Guarde a apikey retornada acima!${NC}"
    else
        echo -e "${RED}✗ Erro ao criar instância${NC}"
    fi
}

# 3) Gerar QR Code
generate_qrcode() {
    echo -e "${BLUE}[3] Gerando QR Code...${NC}"

    echo ""
    echo -e "${YELLOW}Acesse este link no navegador para ver o QR Code:${NC}"
    echo ""
    echo -e "${GREEN}$EVOLUTION_URL/instance/qrcode/$INSTANCE_NAME?apikey=$API_KEY${NC}"
    echo ""

    echo -e "${YELLOW}Ou escaneie o QR Code abaixo (se qrencode estiver instalado):${NC}"
    echo ""

    # Tentar mostrar QR Code no terminal
    if command -v qrencode &> /dev/null; then
        qr_data=$(curl -s "$EVOLUTION_URL/instance/connect/$INSTANCE_NAME" \
            -H "apikey: $API_KEY" | jq -r '.qrcode.code // .code // ""')

        if [ -n "$qr_data" ] && [ "$qr_data" != "null" ]; then
            echo "$qr_data" | qrencode -t UTF8
        else
            echo -e "${YELLOW}QR Code não disponível no momento. Use o link acima.${NC}"
        fi
    else
        echo -e "${YELLOW}qrencode não instalado. Use o link acima.${NC}"
        echo "Para instalar: sudo apt-get install qrencode"
    fi
}

# 4) Verificar conexão
check_connection() {
    echo -e "${BLUE}[4] Verificando status da conexão...${NC}"

    response=$(curl -s "$EVOLUTION_URL/instance/connectionState/$INSTANCE_NAME" \
        -H "apikey: $API_KEY")

    echo "$response" | jq '.'

    state=$(echo "$response" | jq -r '.instance.state // "unknown"')

    if [ "$state" = "open" ]; then
        echo -e "${GREEN}✓ WhatsApp CONECTADO!${NC}"
    elif [ "$state" = "connecting" ]; then
        echo -e "${YELLOW}⏳ WhatsApp conectando...${NC}"
    else
        echo -e "${RED}✗ WhatsApp DESCONECTADO${NC}"
        echo "Execute a opção 3 para gerar novo QR Code"
    fi
}

# 5) Configurar webhook
configure_webhook() {
    echo -e "${BLUE}[5] Configurando webhook para n8n...${NC}"

    read -p "URL do n8n (padrão: http://n8n:5678/webhook/whatsapp-webhook): " webhook_url
    webhook_url=${webhook_url:-http://n8n:5678/webhook/whatsapp-webhook}

    response=$(curl -s -X POST "$EVOLUTION_URL/webhook/set/$INSTANCE_NAME" \
        -H "Content-Type: application/json" \
        -H "apikey: $API_KEY" \
        -d "{
            \"enabled\": true,
            \"url\": \"$webhook_url\",
            \"webhookByEvents\": true,
            \"events\": [
                \"MESSAGES_UPSERT\"
            ]
        }")

    echo "$response" | jq '.'

    echo -e "${GREEN}✓ Webhook configurado!${NC}"
    echo "URL: $webhook_url"
}

# 6) Enviar mensagem de teste
send_test_message() {
    echo -e "${BLUE}[6] Enviando mensagem de teste...${NC}"

    read -p "Número de destino (padrão: $NUMERO_TESTE): " numero
    numero=${numero:-$NUMERO_TESTE}

    read -p "Mensagem (padrão: 'Teste da Evolution API'): " mensagem
    mensagem=${mensagem:-"Teste da Evolution API"}

    response=$(curl -s -X POST "$EVOLUTION_URL/message/sendText/$INSTANCE_NAME" \
        -H "Content-Type: application/json" \
        -H "apikey: $API_KEY" \
        -d "{
            \"number\": \"$numero\",
            \"text\": \"$mensagem\"
        }")

    echo "$response" | jq '.'

    if echo "$response" | jq -e '.key' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Mensagem enviada com sucesso!${NC}"
    else
        echo -e "${RED}✗ Erro ao enviar mensagem${NC}"
    fi
}

# 7) Simular fluxo completo
simulate_flow() {
    echo -e "${BLUE}[7] Simulando fluxo completo via webhook...${NC}"

    echo ""
    echo "Este teste simulará mensagens sendo enviadas para o webhook do n8n"
    echo ""

    N8N_WEBHOOK="http://localhost:5678/webhook/whatsapp-webhook"

    # Mensagem 1: Início
    echo -e "${YELLOW}Enviando: 'Olá'${NC}"
    curl -s -X POST "$N8N_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"event\": \"MESSAGES_UPSERT\",
            \"instance\": \"$INSTANCE_NAME\",
            \"data\": {
                \"key\": {
                    \"remoteJid\": \"${NUMERO_TESTE}@s.whatsapp.net\",
                    \"fromMe\": false
                },
                \"message\": {
                    \"conversation\": \"Olá\"
                },
                \"pushName\": \"Teste\"
            }
        }" | jq '.'

    sleep 2

    # Mensagem 2: Escolher aluguel
    echo -e "${YELLOW}Enviando: '1' (Aluguel)${NC}"
    curl -s -X POST "$N8N_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"event\": \"MESSAGES_UPSERT\",
            \"instance\": \"$INSTANCE_NAME\",
            \"data\": {
                \"key\": {
                    \"remoteJid\": \"${NUMERO_TESTE}@s.whatsapp.net\",
                    \"fromMe\": false
                },
                \"message\": {
                    \"conversation\": \"1\"
                },
                \"pushName\": \"Teste\"
            }
        }" | jq '.'

    sleep 2

    # Mensagem 3: Faixa de preço
    echo -e "${YELLOW}Enviando: '2' (R$ 1.500 a R$ 3.000)${NC}"
    curl -s -X POST "$N8N_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"event\": \"MESSAGES_UPSERT\",
            \"instance\": \"$INSTANCE_NAME\",
            \"data\": {
                \"key\": {
                    \"remoteJid\": \"${NUMERO_TESTE}@s.whatsapp.net\",
                    \"fromMe\": false
                },
                \"message\": {
                    \"conversation\": \"2\"
                },
                \"pushName\": \"Teste\"
            }
        }" | jq '.'

    echo ""
    echo -e "${GREEN}✓ Fluxo de teste enviado!${NC}"
    echo "Verifique os logs do n8n para ver o processamento"
}

# 8) Listar instâncias
list_instances() {
    echo -e "${BLUE}[8] Listando todas as instâncias...${NC}"

    response=$(curl -s "$EVOLUTION_URL/instance/fetchInstances" \
        -H "apikey: $API_KEY")

    echo "$response" | jq '.'
}

# 9) Ver logs
view_logs() {
    echo -e "${BLUE}[9] Logs da Evolution API...${NC}"

    if command -v docker &> /dev/null; then
        docker logs evolution-api --tail 50 -f
    else
        echo -e "${RED}Docker não encontrado${NC}"
    fi
}

# 10) Teste completo (end-to-end)
full_test() {
    echo -e "${BLUE}[10] Teste Completo End-to-End${NC}"
    echo ""
    echo "Este teste vai verificar toda a stack:"
    echo "1. Evolution API"
    echo "2. n8n"
    echo "3. API de Imóveis"
    echo "4. WhatsApp conectado"
    echo ""

    # Teste 1: Evolution API
    echo -e "${YELLOW}[1/4] Testando Evolution API...${NC}"
    test_evolution_running
    echo ""
    pause

    # Teste 2: Conexão WhatsApp
    echo -e "${YELLOW}[2/4] Testando conexão WhatsApp...${NC}"
    check_connection
    echo ""
    pause

    # Teste 3: n8n
    echo -e "${YELLOW}[3/4] Testando n8n...${NC}"
    n8n_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5678")
    if [ "$n8n_response" = "200" ] || [ "$n8n_response" = "401" ]; then
        echo -e "${GREEN}✓ n8n está rodando!${NC}"
    else
        echo -e "${RED}✗ n8n não está acessível!${NC}"
    fi
    echo ""
    pause

    # Teste 4: API de Imóveis
    echo -e "${YELLOW}[4/4] Testando API de Imóveis...${NC}"
    api_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/health")
    if [ "$api_response" = "200" ]; then
        echo -e "${GREEN}✓ API de Imóveis está rodando!${NC}"
    else
        echo -e "${RED}✗ API de Imóveis não está acessível!${NC}"
        echo "Execute: docker-compose up -d api-imoveis"
    fi

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}   Teste Completo Finalizado!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Loop principal
while true; do
    show_menu

    case $option in
        1) test_evolution_running ;;
        2) create_instance ;;
        3) generate_qrcode ;;
        4) check_connection ;;
        5) configure_webhook ;;
        6) send_test_message ;;
        7) simulate_flow ;;
        8) list_instances ;;
        9) view_logs ;;
        10) full_test ;;
        0)
            echo -e "${GREEN}Até logo!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            ;;
    esac

    echo ""
    pause
done
