import requests
from bs4 import BeautifulSoup
import re
import unicodedata

GENERO_MAPA = {
    "animacao": "13026",
    "aventura": "13001",
    "acao": "13025",
    "biopic": "13027",
    "comedia": "13005",
    "comedia dramatica": "13002",
    "drama": "13008",
    "familia": "13036",
    "fantasia": "13012",
    "ficcao cientifica": "13021",
    "historico": "13015",
    "policial": "13018",
    "romance": "13024",
    "suspense": "13023",
    "terror": "13009"
}

def remover_acentos(texto):
    """Remove acentos do texto."""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return ''.join([c for c in texto_normalizado if unicodedata.category(c) != 'Mn'])

def perguntar_preferencias():
    """Pergunta as preferências do usuário."""
    print("Bem-vindo ao sistema de recomendação de filmes!")
    genero = input("Qual gênero de filme você prefere? (Ex: Ação, Comédia, Drama, Terror, etc.): ").strip()
    duracao = input("Você prefere filmes mais longos ou curtos? (Responda: Longos/Curto/Indiferente): ").strip()
    decada = input("Há alguma preferência por década de lançamento? (Ex: 1980, 1990 ou deixe vazio para indiferente): ").strip()
    return genero, duracao, decada

def criar_crawler_adorocinema(genero, duracao, decada):
    """Cria o crawler que busca os filmes baseados nas preferências do usuário."""
    genero_codigo = GENERO_MAPA.get(remover_acentos(genero.lower()), None)
    if not genero_codigo:
        print("Gênero não encontrado. Tente novamente com um gênero válido.")
        return []

    # Monta a URL base com o gênero e a década
    url_base = f"https://www.adorocinema.com/filmes/melhores/genero-{genero_codigo}/"
    if decada:
        url_base += f"decada-{decada}/"

    lista_filmes = []
    pagina = 1

    while len(lista_filmes) < 10:  # Continua até ter 10 filmes
        url = f"{url_base}?page={pagina}"
        
        # Faz a requisição à página
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar a página {pagina}.")
            break
        
        # Parse do conteúdo HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        filmes = soup.find_all('div', class_='card entity-card entity-card-list cf')

        if not filmes:
            print(f"Não foram encontrados filmes na página {pagina}.")
            break  # Se não houver filmes na página, sai do loop
        
        # Para cada filme na página, extraímos as informações
        for filme in filmes:
            # Extrai o nome do filme
            link_tag = filme.find('a', class_='meta-title-link')
            nome = link_tag.text.strip() if link_tag else "Nome não encontrado"
            
            # Extrai o código do filme
            link_filme = link_tag['href'] if link_tag else None
            codigo_filme = link_filme.split("-")[-1].strip("/") if link_filme else None

            # Extrai a sinopse
            sinopse_tag = filme.find('div', class_='content-txt')
            sinopse = sinopse_tag.text.strip() if sinopse_tag else "Sinopse não encontrada"

            # Extrai a duração do filme
            duracao_tag = filme.find('div', class_='meta-body-item meta-body-info')
            duracao_texto = duracao_tag.get_text(strip=True) if duracao_tag else ""

            # Processa a duração e o gênero
            duracao_minutos = 0
            if "h" in duracao_texto:
                horas_part = duracao_texto.split("h")[0].strip()
                duracao_minutos += int(horas_part) * 60 if horas_part.isdigit() else 0

            if "min" in duracao_texto:
                minutos_part = duracao_texto.split("min")[0].strip().split()[-1]
                duracao_minutos += int(minutos_part) if minutos_part.isdigit() else 0

            genero_part = "Gênero não encontrado"
            partes = duracao_texto.split("|")
            if len(partes) > 1:
                genero_part = partes[1].strip()

            # Filtros por duração
            if duracao.lower() != "indiferente":
                if duracao.lower() == "curto" and duracao_minutos > 130:
                    continue
                elif duracao.lower() == "longos" and duracao_minutos <= 130:
                    continue

            # Pega o ano de lançamento da página específica do filme
            url_filme = f"https://www.adorocinema.com/filmes/filme-{codigo_filme}/"
            ano_lancamento = extrair_ano_lancamento(url_filme)

            # Pega os comentários do filme
            comentarios = extrair_comentarios(url_filme)

            # Adiciona o filme à lista
            lista_filmes.append({
                'nome': nome,
                'duracao': duracao_minutos,
                'generos': genero_part,
                'sinopse': sinopse,
                'ano': ano_lancamento,
                'comentarios': comentarios
            })

            # Se já tiver 10 filmes, interrompe a busca
            if len(lista_filmes) == 10:
                break

        # Incrementa a página
        pagina += 1

    return lista_filmes[:10]

def extrair_ano_lancamento(url_filme):
    """Extrai o ano de lançamento de uma página específica de filme."""
    try:
        response = requests.get(url_filme)
        if response.status_code != 200:
            print(f"Erro ao acessar a página do filme: {url_filme}")
            return "Ano não encontrado"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Procura no título da página
        title_tag = soup.find("title")
        if title_tag:
            match = re.search(r"\b(\d{4})\b", title_tag.text)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"Erro ao extrair o ano do filme: {e}")
    return "Ano não encontrado"

def extrair_comentarios(url_filme):
    """Extrai os comentários da página de um filme."""
    try:
        response = requests.get(url_filme)
        if response.status_code != 200:
            print(f"Erro ao acessar a página do filme: {url_filme}")
            return ["Não foi possível acessar os comentários."]
        
        soup = BeautifulSoup(response.text, 'html.parser')
        comentarios_html = soup.find_all('div', class_='review-card-content')  # Ajuste conforme o HTML
        comentarios = []
        for comentario_tag in comentarios_html[:5]:  # Limita a 5 comentários
            texto_completo = comentario_tag.get_text(strip=True)
            comentarios.append(texto_completo)
        return comentarios
    except Exception as e:
        print(f"Erro ao extrair comentários: {e}")
    return ["Erro ao extrair comentários."]

def exibir_recomendacoes(filmes):
    """Exibe as recomendações de filmes."""
    print("\nAqui estão suas recomendações de filmes:\n")
    
    for i, filme in enumerate(filmes, 1):
        print(f"Filme {i}: {filme['nome']}")
        print(f"Duração: {filme['duracao']} minutos")
        print(f"Gêneros: {filme['generos']}")
        print(f"Sinopse: {filme['sinopse']}")
        print(f"Ano de Lançamento: {filme['ano']}")
        print("Comentários:")
        for comentario in filme['comentarios']:
            print(f"- {comentario}")
        print("-" * 30)

def sistema_recomendacao():
    """Sistema principal de recomendação."""
    genero, duracao, decada = perguntar_preferencias()
    filmes = criar_crawler_adorocinema(genero, duracao, decada)
    
    if filmes:
        exibir_recomendacoes(filmes)
    else:
        print("Não foi possível encontrar filmes para as preferências informadas.")

if __name__ == "__main__":
    sistema_recomendacao()
