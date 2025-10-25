# Fluxo de Atendimento WhatsApp para Imobiliárias - n8n

## Descrição

Este é um workflow completo para n8n que automatiza o atendimento de clientes via WhatsApp para imobiliárias. O bot realiza uma triagem completa das necessidades do cliente e apresenta opções de imóveis disponíveis.

## Funcionalidades

### 1. Triagem Inicial
- Identificação do tipo de negócio (Aluguel ou Compra)
- Definição do ticket médio/orçamento

### 2. Coleta de Preferências
- **Número de dormitórios**: 1, 2, 3 ou 4+
- **Tipo de imóvel**: Apartamento, Casa térrea, Sobrado, Cobertura
- **Tipo de sala**: Integrada ou separada
- **Vagas de garagem**: 1, 2, 3+ ou nenhuma
- **Localização**: Bairro ou região preferida

### 3. Busca e Apresentação
- Busca automática no estoque de imóveis
- Envio de detalhes e links dos imóveis disponíveis
- Salvamento do lead no CRM

## Como Importar no n8n

1. Acesse seu n8n
2. Clique em **"Workflows"** no menu lateral
3. Clique em **"Import from File"** ou **"Add Workflow" > "Import from File"**
4. Selecione o arquivo `whatsapp-imobiliaria-flow.json`
5. Clique em **"Import"**

## Configurações Necessárias

### 1. Integração WhatsApp

Você precisa configurar uma das seguintes opções:

#### Opção A: WhatsApp Business API
- Configure as credenciais do WhatsApp Business API no n8n
- Atualize os nós de mensagem com suas credenciais

#### Opção B: API de terceiros (Evolution API, Baileys, etc.)
- Configure a API escolhida
- Substitua os nós do tipo "whatsapp" por nós HTTP Request apontando para sua API

### 2. API de Busca de Imóveis

No nó **"Buscar Imóveis no Estoque"**, atualize:

```javascript
URL: https://sua-api-imoveis.com/buscar
```

A API deve aceitar os seguintes parâmetros:
- `tipo_negocio`: "aluguel" ou "compra"
- `faixa_preco`: string identificando a faixa
- `dormitorios`: número de dormitórios
- `tipo_imovel`: tipo do imóvel
- `tipo_sala`: "integrada", "separada" ou "tanto_faz"
- `vagas`: número de vagas
- `localizacao`: string com bairro/região

E retornar um JSON no formato:

```json
{
  "imoveis": [
    {
      "titulo": "Apartamento Moderno no Centro",
      "endereco": "Rua das Flores, 123 - Centro",
      "preco": "450000",
      "dormitorios": 2,
      "vagas": 1,
      "area_m2": 65,
      "link": "https://sua-imobiliaria.com/imovel/123",
      "descricao": "Apartamento novo com acabamento de primeira"
    }
  ]
}
```

### 3. Integração com CRM (Opcional)

No nó **"Salvar Lead no CRM"**, configure:

```javascript
URL: https://sua-api-crm.com/leads
```

Este nó salva todas as preferências do cliente para follow-up posterior.

## Fluxo de Conversação

### Exemplo de Interação

```
Bot: Olá! 👋 Bem-vindo à nossa imobiliária!
     Você está buscando:
     1️⃣ - Aluguel
     2️⃣ - Compra

Cliente: 1

Bot: Perfeito! Você escolheu aluguel.
     Qual é o seu orçamento/ticket médio?
     [opções de faixa de preço]

Cliente: 6

Bot: Ótimo! Agora me conte mais sobre o imóvel...
     Quantos dormitórios você precisa?
     [opções de dormitórios]

[... continua a triagem ...]

Bot: 🎉 Encontrei 3 imóveis que correspondem ao seu perfil!

Bot: 🏡 *Apartamento Moderno no Centro*
     📍 Localização: Rua das Flores, 123
     💰 Valor: R$ 2.500
     🛏️ Dormitórios: 2
     ...
```

## Personalização

### Modificar Faixas de Preço

Edite o nó **"Mensagem Orçamento"** para ajustar as faixas de acordo com seu mercado local.

### Adicionar Mais Critérios

Você pode adicionar novos critérios como:
- Área mínima (m²)
- Aceita pets
- Mobiliado/não mobiliado
- Condomínio com piscina/academia
- Quartos com suíte

Basta:
1. Adicionar um novo nó de mensagem
2. Adicionar nó de decisão
3. Salvar a preferência
4. Incluir no parâmetro da busca

### Customizar Mensagens

Todas as mensagens podem ser editadas nos nós do tipo "Mensagem". Você pode:
- Adicionar emojis
- Mudar o tom de voz
- Incluir informações da sua imobiliária
- Adicionar URLs de site/redes sociais

## Armazenamento de Estado

Este workflow é simplificado e funciona em uma única execução. Para um sistema mais robusto com múltiplas mensagens, considere:

1. **Usar banco de dados**: Adicionar nós do Redis ou MongoDB para armazenar o estado da conversa
2. **Usar variáveis de fluxo**: Configurar sticky sessions
3. **Implementar máquina de estados**: Controlar melhor as etapas da conversa

## Exemplo de Implementação com Estado

```javascript
// Nó de verificação de estado
const clienteId = $json.cliente_numero;
const estadoAtual = await redis.get(`cliente:${clienteId}:estado`);

if (!estadoAtual) {
  // Primeiro contato
  return { etapa: 'boas_vindas' };
} else {
  // Cliente retornando
  return JSON.parse(estadoAtual);
}
```

## Melhorias Sugeridas

1. **Validação de entrada**: Adicionar validação para garantir que o cliente digite números válidos
2. **Opção de voltar**: Permitir que o cliente volte para etapas anteriores
3. **Salvar busca**: Permitir que o cliente salve suas preferências para buscas futuras
4. **Notificações**: Enviar notificações quando novos imóveis corresponderem ao perfil
5. **Agendamento**: Permitir agendamento de visitas diretamente pelo WhatsApp
6. **Fotos**: Enviar fotos dos imóveis junto com os detalhes
7. **Tour virtual**: Incluir links para tours virtuais 360°
8. **Calculadora**: Adicionar calculadora de financiamento

## Manutenção

### Logs
Configure logs para monitorar:
- Taxa de conversão (leads gerados vs. conversas iniciadas)
- Etapa onde mais clientes abandonam
- Tipos de imóveis mais buscados

### Testes
Recomenda-se testar:
- Todos os caminhos de decisão
- Casos onde não há imóveis disponíveis
- Validação de entrada do usuário
- Timeout de conversação

## Suporte

Para problemas com:
- **n8n**: https://docs.n8n.io
- **WhatsApp API**: Consulte documentação do seu provedor
- **Este workflow**: Abra uma issue no repositório

## Licença

Este workflow é fornecido como está, para uso livre.

## Contribuições

Sinta-se à vontade para melhorar este workflow e compartilhar suas melhorias!
