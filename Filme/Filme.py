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
        
        # Tenta encontrar os filmes com uma estrutura alternativa
        for item in soup.find_all('div', class_='entity-card-list-item'):
            # Procura o título e sinopse
            titulo_element = item.find('a', class_='meta-title-link')
            sinopse_element = item.find('div', class_='synopsis')
            
            # Verifica se ambos os elementos foram encontrados
            if titulo_element and sinopse_element:
                titulo = titulo_element.text.strip()
                sinopse = sinopse_element.text.strip()
                
                filmes.append({
                    'titulo': titulo,
                    'sinopse': sinopse,
                    'comentarios': 'Comentários sobre o filme não foram capturados.'
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
