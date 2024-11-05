import requests
from bs4 import BeautifulSoup

def recomendar_filmes(genero):
    # Define a URL do site com base no gênero de filmes escolhido
    url = f"https://www.adorocinema.com/filmes/{genero.lower()}"
    
    # Faz uma requisição à página
    response = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        filmes = []
        
        # Extrai os filmes da página
        for item in soup.find_all('div', class_='card card-entity card-entity-list cf'):
            titulo = item.find('h2', class_='meta-title').text.strip()
            sinopse = item.find('div', class_='content-txt').text.strip()
            
            filmes.append({
                'titulo': titulo,
                'sinopse': sinopse,
                'comentarios': 'Comentários sobre o filme não foram capturados.'  # Ponto de melhoria
            })
        
        # Retorna até 5 filmes como recomendação
        return filmes[:5]
    
    else:
        print("Não foi possível acessar o site para buscar filmes.")
        return []

# Exemplo de uso da função
genero = input("Digite o gênero do filme que você deseja (ex: acao, drama, comedia): ")
filmes_recomendados = recomendar_filmes(genero)

# Exibe os filmes recomendados
if filmes_recomendados:
    print("\nAqui estão algumas recomendações de filmes para você:\n")
    for i, filme in enumerate(filmes_recomendados, 1):
        print(f"{i}. Título: {filme['titulo']}")
        print(f"   Sinopse: {filme['sinopse']}")
        print(f"   Comentários: {filme['comentarios']}")
        print()
else:
    print("Nenhuma recomendação encontrada.")
