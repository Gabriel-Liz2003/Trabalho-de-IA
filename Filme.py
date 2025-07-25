import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import os
 
 #Lista de generos pra busca
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

# Mapeamento de gêneros para a API do TMDb
GENERO_MAPA_TMDB = {
    "acao": 28,
    "aventura": 12,
    "animacao": 16,
    "comedia": 35,
    "drama": 18,
    "familia": 10751,
    "fantasia": 14,
    "ficcao cientifica": 878,
    "historico": 36,
    "policial": 80,
    "romance": 10749,
    "suspense": 53,
    "terror": 27
}

#Metodo pra remover acentos do texto 
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

    url_base = f"https://www.adorocinema.com/filmes/melhores/genero-{genero_codigo}/"
    if decada:
        url_base += f"decada-{decada}/"

    lista_filmes = []
    pagina = 1
    max_paginas = 6  # Define o limite máximo de páginas

    while len(lista_filmes) < 10 and pagina <= max_paginas:  # Continua até 10 filmes ou 6 páginas
        url = f"{url_base}?page={pagina}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar a página {pagina}.")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        filmes = soup.find_all('div', class_='card entity-card entity-card-list cf')

        if not filmes:
            print(f"Fim das páginas alcançado ou nenhuma informação na página {pagina}.")
            break
        
        for filme in filmes:
            link_tag = filme.find('a', class_='meta-title-link')
            nome = link_tag.text.strip() if link_tag else "Nome não encontrado"
            link_filme = link_tag['href'] if link_tag else None
            codigo_filme = link_filme.split("-")[-1].strip("/") if link_filme else None

            # Extrai a imagem do filme
            img_tag = filme.find('img', class_='thumbnail-img')
            imagem_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else (
                img_tag['src'] if img_tag and 'src' in img_tag.attrs else "Imagem não encontrada"
            )

            sinopse_tag = filme.find('div', class_='content-txt')
            if sinopse_tag:
                texto_completo = sinopse_tag.find('span', class_='hidden-text')
                sinopse = texto_completo.get_text(strip=True) if texto_completo else sinopse_tag.get_text(strip=True)
            else:
                sinopse = "Sinopse não encontrada"

            duracao_tag = filme.find('div', class_='meta-body-item meta-body-info')
            duracao_texto = duracao_tag.get_text(strip=True) if duracao_tag else ""
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

            if duracao.lower() != "indiferente":
                if duracao.lower() == "curto" and duracao_minutos > 130:
                    continue
                elif duracao.lower() == "longos" and duracao_minutos <= 130:
                    continue

            url_filme = f"https://www.adorocinema.com/filmes/filme-{codigo_filme}/"
            ano_lancamento = extrair_ano_lancamento(url_filme)
            comentarios = extrair_comentarios(url_filme)

            lista_filmes.append({
                'nome': nome,
                'imagem': imagem_url,
                'duracao': duracao_minutos,
                'generos': genero_part,
                'sinopse': sinopse,
                'ano': ano_lancamento,
                'comentarios': comentarios,
                'url': url_filme
            })

            if len(lista_filmes) == 10:
                break

        pagina += 1

    if len(lista_filmes) < 10:
        print(f"Apenas {len(lista_filmes)} filmes foram encontrados no total.")
    return lista_filmes


def criar_crawler_tmdb(genero, duracao, decada):
    """Busca filmes usando a API do TMDb."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("TMDB_API_KEY não definido no ambiente.")
        return []

    genero_codigo = GENERO_MAPA_TMDB.get(remover_acentos(genero.lower()))
    if not genero_codigo:
        print("Gênero não encontrado para o TMDb.")
        return []

    params = {
        "api_key": api_key,
        "language": "pt-BR",
        "with_genres": genero_codigo,
        "page": 1
    }

    if decada:
        params["primary_release_date.gte"] = f"{decada}-01-01"
        params["primary_release_date.lte"] = f"{int(decada)+9}-12-31"

    if duracao.lower() == "curto":
        params["with_runtime.lte"] = 130
    elif duracao.lower() == "longos":
        params["with_runtime.gte"] = 131

    lista_filmes = []

    while len(lista_filmes) < 10 and params["page"] <= 6:
        response = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
        if response.status_code != 200:
            print("Erro ao acessar a API do TMDb.")
            break

        dados = response.json()
        resultados = dados.get("results", [])

        if not resultados:
            break

        for filme in resultados:
            titulo = filme.get("title")
            sinopse = filme.get("overview", "Sinopse não encontrada")
            ano = filme.get("release_date", "").split("-")[0]
            duracao_filme = filme.get("runtime", 0)  # pode não vir preenchido
            imagem = film_poster_url = f"https://image.tmdb.org/t/p/w500{filme.get('poster_path')}" if filme.get("poster_path") else ""
            url = f"https://www.themoviedb.org/movie/{filme.get('id')}"

            lista_filmes.append({
                "nome": titulo,
                "imagem": imagem,
                "duracao": duracao_filme,
                "generos": genero,
                "sinopse": sinopse,
                "ano": ano,
                "comentarios": ["Comentários indisponíveis."],
                "url": url,
            })

            if len(lista_filmes) == 10:
                break

        params["page"] += 1

    return lista_filmes

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
        print(f"Imagem: {filme['imagem']}")
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
    fonte = input("Escolha a fonte (adorocinema/tmdb): ").strip().lower() or "adorocinema"
    if fonte == "tmdb":
        filmes = criar_crawler_tmdb(genero, duracao, decada)
    else:
        filmes = criar_crawler_adorocinema(genero, duracao, decada)
    
    if filmes:
        exibir_recomendacoes(filmes)
    else:
        print("Não foi possível encontrar filmes para as preferências informadas.")

if __name__ == "__main__":
    sistema_recomendacao()
