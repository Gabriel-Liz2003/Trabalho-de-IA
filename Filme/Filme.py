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
        # Extrai o link e o nome do filme
        link_tag = filme.find('a', class_='meta-title-link')
        nome = link_tag.text.strip() if link_tag else "Nome não encontrado"
        link = "https://www.adorocinema.com" + link_tag['href'] if link_tag else ""

        # Extrai a duração do filme
        duracao_tag = filme.find('div', class_='meta-body-item meta-body-info')
        duracao_texto = duracao_tag.text.strip() if duracao_tag else ""
        horas, minutos = 0, 0
        if "h" in duracao_texto:
            partes = duracao_texto.split("h")
            horas = int(partes[0].strip()) if partes[0].strip().isdigit() else 0
            duracao_texto = partes[1] if len(partes) > 1 else ""
        if "min" in duracao_texto:
            minutos_text = duracao_texto.replace("min", "").strip()
            minutos = re.search(r'\d{2}', duracao_texto)
            minutos = int(minutos_text) if minutos_text.isdigit() else 0
        duracao_minutos = horas * 60 + minutos

        # Extrai o ano de lançamento
        ano_tag = filme.find('span', class_='date')
        ano_lancamento = int(ano_tag.text.strip()[-4:]) if ano_tag and ano_tag.text.strip()[-4:].isdigit() else "Ano não encontrado"

        # Extrai os gêneros do filme
        genero_links = filme.find_all('a', class_='xXx dark-grey-link')
        generos = [g.text.strip() for g in genero_links if '/genero-' in g['href']] if genero_links else ["Gênero não encontrado"]

        # Filtros por duração
        if duracao.lower() != "indiferente":
            if duracao.lower() == "curto" and duracao_minutos > 130:
                continue
            elif duracao.lower() == "longos" and duracao_minutos <= 130:
                continue

        # Adiciona o filme à lista de recomendações
        lista_filmes.append({
            'nome': nome,
            'link': link,
            'ano': ano_lancamento,
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
        print(f"Link: {filme['link']}")
        print(f"Ano: {filme['ano']}")
        print(f"Duração: {filme['duracao']} minutos")
        print(f"Gêneros: {', '.join(filme['generos'])}")
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