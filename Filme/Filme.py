import requests
from bs4 import BeautifulSoup
import re

GENERO_MAPA = {
    "Animação": "13026",
    "Aventura": "13001",
    "Ação": "13025",
    "Biopic": "13027",
    "Comédia": "13005",
    "Comédia dramática": "13002",
    "Drama": "13008",
    "Família": "13036",
    "Fantasia": "13012",
    "Ficção Científica": "13021",
    "Histórico": "13015",
    "Policial": "13018",
    "Romance": "13024",
    "Suspense": "13023",
    "Terror": "13009"
}

def perguntar_preferencias():
    print("Bem-vindo ao sistema de recomendação de filmes!")
    genero = input("Qual gênero de filme você prefere? (Ex: Ação, Comédia, Drama, Terror, etc.): ").strip()
    duracao = input("Você prefere filmes mais longos ou curtos? (Responda: Longos/Curto/Indiferente): ").strip()
    decada = input("Há alguma preferência por década de lançamento? (Ex: 1980, 1990 ou deixe vazio para indiferente): ").strip()
    return genero, duracao, decada

def criar_crawler_adorocinema(genero, duracao, decada):
    genero_codigo = GENERO_MAPA.get(genero, None)
    if not genero_codigo:
        print("Gênero não encontrado. Tente novamente com um gênero válido.")
        return []

    # Monta a URL com gênero e década
    url = f"https://www.adorocinema.com/filmes/melhores/genero-{genero_codigo}/"
    if decada:
        url += f"decada-{decada}/"

    response = requests.get(url)
    if response.status_code != 200:
        print("Erro ao acessar o site.")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    filmes = soup.find_all('div', class_='card entity-card entity-card-list cf')
    lista_filmes = []

    for filme in filmes:
        # Extrai o nome do filme
        link_tag = filme.find('a', class_='meta-title-link')
        nome = link_tag.text.strip() if link_tag else "Nome não encontrado"

        # Extrai a duração do filme
        duracao_tag = filme.find('div', class_='meta-body-item meta-body-info')
        duracao_texto = duracao_tag.get_text(strip=True) if duracao_tag else ""
        
        # Extrai horas e minutos
        duracao_minutos = 0
        if "h" in duracao_texto:
            horas_part = duracao_texto.split("h")[0].strip()
            duracao_minutos += int(horas_part) * 60 if horas_part.isdigit() else 0

        if "min" in duracao_texto:
            minutos_part = duracao_texto.split("min")[0].strip().split()[-1]
            duracao_minutos += int(minutos_part) if minutos_part.isdigit() else 0

        # Extrai os gêneros do filme
        genero_container = filme.find('div', class_='meta-body-item meta-body-info')
        genero_links = genero_container.find_all('a', class_='xxx dark-grey-link') if genero_container else []
        generos = [g.text.strip() for g in genero_links]

        # Filtros por duração
        if duracao.lower() != "indiferente":
            if duracao.lower() == "curto" and duracao_minutos > 130:
                continue
            elif duracao.lower() == "longos" and duracao_minutos <= 130:
                continue

        # Adiciona o filme à lista de recomendações
        lista_filmes.append({
            'nome': nome,
            'duracao': duracao_minutos,
            'generos': generos
        })

        # Limita a 5 filmes recomendados
        if len(lista_filmes) == 5:
            break

    return lista_filmes

def exibir_recomendacoes(filmes):
    print("\nAqui estão suas recomendações de filmes:\n")
    
    for i, filme in enumerate(filmes, 1):
        print(f"Filme {i}: {filme['nome']}")
        print(f"Duração: {filme['duracao']} minutos")
        print(f"Gêneros: {', '.join(filme['generos']) if filme['generos'] else 'Gênero não encontrado'}")
        print("\n")

def sistema_recomendacao():
    genero, duracao, decada = perguntar_preferencias()
    filmes = criar_crawler_adorocinema(genero, duracao, decada)
    
    if filmes:
        exibir_recomendacoes(filmes)
    else:
        print("Não foi possível encontrar filmes para as preferências informadas.")

if __name__ == "__main__":
    sistema_recomendacao()
