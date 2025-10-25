"""
API de Busca de Imóveis - Exemplo para integração com n8n
Servidor Flask simples para buscar imóveis conforme critérios do WhatsApp Bot
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# Banco de dados simulado (em produção, use MongoDB, PostgreSQL, etc.)
IMOVEIS_DB = [
    {
        "id": 1001,
        "titulo": "Apartamento Moderno com Vista",
        "tipo_negocio": "aluguel",
        "tipo_imovel": "apartamento",
        "endereco": "Rua das Palmeiras, 456",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "preco": 2800,
        "dormitorios": 2,
        "suites": 1,
        "banheiros": 2,
        "vagas": 1,
        "area_m2": 72,
        "tipo_sala": "integrada",
        "link": "https://sua-imobiliaria.com/imovel/1001",
        "descricao": "Lindo apartamento com 2 dormitórios sendo 1 suíte, sala integrada com cozinha americana.",
        "fotos": [
            "https://sua-imobiliaria.com/fotos/1001/foto1.jpg",
            "https://sua-imobiliaria.com/fotos/1001/foto2.jpg"
        ],
        "caracteristicas": {
            "condominio": 850,
            "iptu": 120,
            "mobiliado": False,
            "aceita_pets": True,
            "andar": 8,
            "elevador": True,
            "sacada": True,
            "churrasqueira": True,
            "piscina": True,
            "academia": True
        },
        "status": "disponivel"
    },
    {
        "id": 1002,
        "titulo": "Casa Térrea Espaçosa",
        "tipo_negocio": "compra",
        "tipo_imovel": "casa_terrea",
        "endereco": "Rua dos Jardins, 123",
        "bairro": "Jardim das Flores",
        "cidade": "São Paulo",
        "preco": 650000,
        "dormitorios": 3,
        "suites": 1,
        "banheiros": 2,
        "vagas": 2,
        "area_m2": 180,
        "tipo_sala": "separada",
        "link": "https://sua-imobiliaria.com/imovel/1002",
        "descricao": "Casa térrea com 3 dormitórios, quintal amplo, área gourmet completa.",
        "fotos": [
            "https://sua-imobiliaria.com/fotos/1002/foto1.jpg"
        ],
        "caracteristicas": {
            "iptu": 250,
            "mobiliado": False,
            "aceita_pets": True,
            "churrasqueira": True,
            "quintal": True,
            "area_gourmet": True
        },
        "status": "disponivel"
    },
    {
        "id": 1003,
        "titulo": "Apartamento Compacto no Centro",
        "tipo_negocio": "aluguel",
        "tipo_imovel": "apartamento",
        "endereco": "Av. Principal, 789",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "preco": 1950,
        "dormitorios": 2,
        "suites": 0,
        "banheiros": 1,
        "vagas": 1,
        "area_m2": 55,
        "tipo_sala": "integrada",
        "link": "https://sua-imobiliaria.com/imovel/1003",
        "descricao": "Apartamento compacto e funcional, ideal para casal.",
        "fotos": [
            "https://sua-imobiliaria.com/fotos/1003/foto1.jpg"
        ],
        "caracteristicas": {
            "condominio": 480,
            "iptu": 75,
            "mobiliado": True,
            "aceita_pets": True,
            "andar": 3
        },
        "status": "disponivel"
    },
    {
        "id": 1004,
        "titulo": "Cobertura Duplex de Luxo",
        "tipo_negocio": "compra",
        "tipo_imovel": "cobertura",
        "endereco": "Rua Premium, 1000",
        "bairro": "Zona Sul",
        "cidade": "São Paulo",
        "preco": 2500000,
        "dormitorios": 4,
        "suites": 3,
        "banheiros": 5,
        "vagas": 3,
        "area_m2": 320,
        "tipo_sala": "integrada",
        "link": "https://sua-imobiliaria.com/imovel/1004",
        "descricao": "Cobertura duplex com acabamento de primeira, piscina privativa.",
        "fotos": [
            "https://sua-imobiliaria.com/fotos/1004/foto1.jpg"
        ],
        "caracteristicas": {
            "condominio": 3500,
            "iptu": 800,
            "mobiliado": False,
            "aceita_pets": True,
            "piscina_privativa": True,
            "churrasqueira": True,
            "elevador_privativo": True,
            "vista_mar": True
        },
        "status": "disponivel"
    },
    {
        "id": 1005,
        "titulo": "Sobrado Novo em Condomínio",
        "tipo_negocio": "compra",
        "tipo_imovel": "sobrado",
        "endereco": "Condomínio Residencial Park, 45",
        "bairro": "Zona Oeste",
        "cidade": "São Paulo",
        "preco": 890000,
        "dormitorios": 3,
        "suites": 2,
        "banheiros": 3,
        "vagas": 2,
        "area_m2": 200,
        "tipo_sala": "integrada",
        "link": "https://sua-imobiliaria.com/imovel/1005",
        "descricao": "Sobrado novo em condomínio fechado, acabamento moderno.",
        "fotos": [
            "https://sua-imobiliaria.com/fotos/1005/foto1.jpg"
        ],
        "caracteristicas": {
            "condominio": 650,
            "iptu": 180,
            "mobiliado": False,
            "aceita_pets": True,
            "churrasqueira": True,
            "area_gourmet": True,
            "condominio_fechado": True,
            "portaria_24h": True
        },
        "status": "disponivel"
    }
]


def get_faixa_preco(faixa_codigo: str) -> tuple:
    """Retorna o range de preços baseado no código da faixa"""
    faixas = {
        # Compra
        "ate_500k": (0, 500000),
        "500k_1m": (500000, 1000000),
        "1m_2m": (1000000, 2000000),
        "acima_2m": (2000000, float('inf')),
        # Aluguel
        "ate_1500": (0, 1500),
        "1500_3000": (1500, 3000),
        "3000_5000": (3000, 5000),
        "acima_5000": (5000, float('inf'))
    }
    return faixas.get(faixa_codigo, (0, float('inf')))


def filtrar_imoveis(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filtra imóveis baseado nos critérios recebidos"""
    resultados = IMOVEIS_DB.copy()

    # Filtro: tipo de negócio
    if filtros.get('tipo_negocio'):
        resultados = [i for i in resultados
                     if i['tipo_negocio'] == filtros['tipo_negocio']]

    # Filtro: faixa de preço
    if filtros.get('faixa_preco'):
        min_preco, max_preco = get_faixa_preco(filtros['faixa_preco'])
        resultados = [i for i in resultados
                     if min_preco <= i['preco'] <= max_preco]

    # Filtro: número de dormitórios
    if filtros.get('dormitorios'):
        dorm = int(filtros['dormitorios'])
        if dorm >= 4:
            resultados = [i for i in resultados if i['dormitorios'] >= 4]
        else:
            resultados = [i for i in resultados if i['dormitorios'] == dorm]

    # Filtro: tipo de imóvel
    if filtros.get('tipo_imovel') and filtros['tipo_imovel'] != 'todos':
        resultados = [i for i in resultados
                     if i['tipo_imovel'] == filtros['tipo_imovel']]

    # Filtro: tipo de sala
    if filtros.get('tipo_sala') and filtros['tipo_sala'] != 'tanto_faz':
        resultados = [i for i in resultados
                     if i.get('tipo_sala') == filtros['tipo_sala']]

    # Filtro: vagas de garagem
    if filtros.get('vagas'):
        vagas = int(filtros['vagas'])
        if vagas == 0:
            pass  # Qualquer quantidade serve
        elif vagas >= 3:
            resultados = [i for i in resultados if i['vagas'] >= 3]
        else:
            resultados = [i for i in resultados if i['vagas'] >= vagas]

    # Filtro: localização (busca no bairro)
    if filtros.get('localizacao'):
        loc = filtros['localizacao'].lower()
        resultados = [i for i in resultados
                     if loc in i['bairro'].lower() or loc in i['cidade'].lower()]

    # Apenas imóveis disponíveis
    resultados = [i for i in resultados if i['status'] == 'disponivel']

    return resultados


@app.route('/buscar', methods=['GET'])
def buscar_imoveis():
    """
    Endpoint principal de busca de imóveis

    Parâmetros esperados:
    - tipo_negocio: 'aluguel' ou 'compra'
    - faixa_preco: código da faixa (ex: 'ate_500k', '1500_3000')
    - dormitorios: número de dormitórios
    - tipo_imovel: 'apartamento', 'casa_terrea', 'sobrado', 'cobertura', 'todos'
    - tipo_sala: 'integrada', 'separada', 'tanto_faz'
    - vagas: número de vagas
    - localizacao: nome do bairro ou região
    """
    try:
        # Capturar parâmetros da query string
        filtros = {
            'tipo_negocio': request.args.get('tipo_negocio'),
            'faixa_preco': request.args.get('faixa_preco'),
            'dormitorios': request.args.get('dormitorios'),
            'tipo_imovel': request.args.get('tipo_imovel'),
            'tipo_sala': request.args.get('tipo_sala'),
            'vagas': request.args.get('vagas'),
            'localizacao': request.args.get('localizacao')
        }

        # Filtrar imóveis
        imoveis_encontrados = filtrar_imoveis(filtros)

        # Preparar resposta
        resposta = {
            "imoveis": imoveis_encontrados,
            "total_encontrados": len(imoveis_encontrados),
            "filtros_aplicados": filtros,
            "mensagem": f"Encontramos {len(imoveis_encontrados)} imóveis que correspondem aos seus critérios",
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({
            "erro": str(e),
            "mensagem": "Erro ao buscar imóveis"
        }), 500


@app.route('/imovel/<int:imovel_id>', methods=['GET'])
def get_imovel(imovel_id):
    """Retorna detalhes de um imóvel específico"""
    imovel = next((i for i in IMOVEIS_DB if i['id'] == imovel_id), None)

    if imovel:
        return jsonify(imovel), 200
    else:
        return jsonify({"erro": "Imóvel não encontrado"}), 404


@app.route('/leads', methods=['POST'])
def salvar_lead():
    """
    Salva um lead de cliente interessado
    Endpoint para integração com CRM
    """
    try:
        dados = request.get_json()

        # Simular salvamento (em produção, salvar no banco de dados)
        lead = {
            "id": hash(dados.get('telefone', '')),
            "telefone": dados.get('telefone'),
            "tipo_negocio": dados.get('tipo_negocio'),
            "faixa_preco": dados.get('faixa_preco'),
            "dormitorios": dados.get('dormitorios'),
            "tipo_imovel": dados.get('tipo_imovel'),
            "preferencias": dados.get('preferencias'),
            "data_atendimento": dados.get('data_atendimento'),
            "status": "novo",
            "criado_em": datetime.now().isoformat()
        }

        print(f"Lead salvo: {lead}")

        return jsonify({
            "mensagem": "Lead salvo com sucesso",
            "lead_id": lead['id']
        }), 201

    except Exception as e:
        return jsonify({
            "erro": str(e),
            "mensagem": "Erro ao salvar lead"
        }), 500


@app.route('/stats', methods=['GET'])
def estatisticas():
    """Retorna estatísticas dos imóveis"""
    total = len(IMOVEIS_DB)
    disponiveis = len([i for i in IMOVEIS_DB if i['status'] == 'disponivel'])

    por_tipo = {}
    for imovel in IMOVEIS_DB:
        tipo = imovel['tipo_imovel']
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return jsonify({
        "total_imoveis": total,
        "imoveis_disponiveis": disponiveis,
        "por_tipo_imovel": por_tipo,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Endpoint raiz com documentação básica"""
    return jsonify({
        "mensagem": "API de Imóveis - Integração WhatsApp Bot",
        "versao": "1.0",
        "endpoints": {
            "GET /buscar": "Buscar imóveis com filtros",
            "GET /imovel/<id>": "Detalhes de um imóvel específico",
            "POST /leads": "Salvar lead de cliente",
            "GET /stats": "Estatísticas dos imóveis",
            "GET /health": "Health check"
        },
        "documentacao": "https://github.com/sua-imobiliaria/api-docs"
    }), 200


if __name__ == '__main__':
    print("🏠 API de Imóveis iniciada!")
    print("📍 Rodando em: http://localhost:5000")
    print("📚 Documentação: http://localhost:5000/")
    print("\nEndpoints disponíveis:")
    print("  GET  /buscar - Buscar imóveis")
    print("  GET  /imovel/<id> - Detalhes do imóvel")
    print("  POST /leads - Salvar lead")
    print("  GET  /stats - Estatísticas")
    print("  GET  /health - Health check")

    app.run(debug=True, host='0.0.0.0', port=5000)
