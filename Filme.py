import requests
from bs4 import BeautifulSoup

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
    ano = input("Há alguma preferência por ano de lançamento? (Digite o ano ou deixe vazio para indiferente): ").strip()
    return genero, duracao, ano

def obter_detalhes_filme(link):
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Erro ao acessar o site para o link: {link}")
        return "Nome não encontrado", "Ano não encontrado", 0, ["Gênero não encontrado"]

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraindo o nome do filme
    nome_tag = soup.find('h1', class_='titlebar-title')
    nome = nome_tag.text.strip() if nome_tag else "Nome não encontrado"
    if nome == "Nome não encontrado":
        print("Erro: Nome do filme não encontrado")
    else:
        print(f"Nome do filme extraído: {nome}")

    # Extraindo o ano
    ano_tag = soup.find('span', class_='date')
    ano_lancamento = int(ano_tag.text.strip()[-4:]) if ano_tag and ano_tag.text.strip()[-4:].isdigit() else "Ano não encontrado"
    if ano_lancamento == "Ano não encontrado":
        print("Erro: Ano de lançamento não encontrado")
    else:
        print(f"Ano de lançamento extraído: {ano_lancamento}")

    # Extraindo duração
    duracao_texto = ""
    duracao_minutos = 0

    duracao_tag = soup.find('div', class_='meta-body-item meta-body-info')
    if duracao_tag:
        duracao_texto = duracao_tag.text.strip()
        
        # Tratamento para extração da duração em horas e minutos
        if "h" in duracao_texto or "min" in duracao_texto:
            horas = 0
            minutos = 0

            if "h" in duracao_texto:
                partes = duracao_texto.split("h")
                horas = int(partes[0].strip()) if partes[0].strip().isdigit() else 0
                duracao_texto = partes[1] if len(partes) > 1 else ""

            if "min" in duracao_texto:
                minutos_text = duracao_texto.replace("min", "").strip()
                minutos = int(minutos_text) if minutos_text.isdigit() else 0

            duracao_minutos = horas * 60 + minutos
        print(f"Duração extraída: {duracao_minutos} minutos")

    # Extraindo gêneros
    generos_tags = duracao_tag.find_all('span', class_='spacer') if duracao_tag else []
    generos = [g.previous_sibling.text.strip() for g in generos_tags if g.previous_sibling] if generos_tags else ["Gênero não encontrado"]
    if generos == ["Gênero não encontrado"]:
        print("Erro: Gêneros não encontrados")
    else:
        print(f"Gêneros extraídos: {generos}")

    return nome, ano_lancamento, duracao_minutos, generos



def criar_crawler_adorocinema(genero, duracao, ano):
    genero_codigo = GENERO_MAPA.get(genero, None)
    if not genero_codigo:
        print("Gênero não encontrado. Tente novamente com um gênero válido.")
        return []

    url = f"https://www.adorocinema.com/filmes/melhores/genero-{genero_codigo}/"
    response = requests.get(url)
    if response.status_code != 200:
        print("Erro ao acessar o site.")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    filmes = soup.find_all('div', class_='card entity-card entity-card-list cf')
    lista_filmes = []

    for filme in filmes:
        link_tag = filme.find('a', class_='meta-title-link')
        if not link_tag:
            continue
        
        # Montando o link completo
        link = "https://www.adorocinema.com" + link_tag['href']
        
        # Extraindo detalhes da página do filme
        nome, ano_lancamento, duracao_minutos, generos = obter_detalhes_filme(link)

        # Filtrar por ano
        if ano and str(ano_lancamento) != ano:
            continue

        # Filtrar por duração
        if duracao.lower() != "indiferente":
            if duracao.lower() == "curto" and duracao_minutos > 130:
                continue
            elif duracao.lower() == "longos" and duracao_minutos <= 130:
                continue
        
        # Adicionar filme à lista
        lista_filmes.append({
            'nome': nome,
            'link': link,
            'ano': ano_lancamento,
            'duracao': duracao_minutos,
            'generos': generos
        })

        # Limite de 5 filmes recomendados
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
    genero, duracao, ano = perguntar_preferencias()
    filmes = criar_crawler_adorocinema(genero, duracao, ano)
    
    if filmes:
        exibir_recomendacoes(filmes)
    else:
        print("Não foi possível encontrar filmes para as preferências informadas.")

if __name__ == "__main__":
    sistema_recomendacao()
