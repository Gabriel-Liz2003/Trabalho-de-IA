// Quando o formulário com o ID 'preferencesForm' for enviado, faça o seguinte:
document.getElementById('preferencesForm').addEventListener('submit', function(event) {
    // Não deixa o formulário recarregar a página
    event.preventDefault();

    // Pega os valores dos campos do formulário
    const genero = document.getElementById('genero').value;
    const duracao = document.getElementById('duracao').value;
    const ano = document.getElementById('ano').value;

    // Manda uma requisição POST pro servidor com os dados do formulário
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // Envia os dados do formulário como JSON
        body: JSON.stringify({ genero, duracao, ano })
    })
    // Quando o servidor responder, transforma a resposta em JSON
    .then(response => response.json())
    // Chama a função que mostra as recomendações de filmes
    .then(data => {
        displayRecommendations(data);
    })
    // Se der erro, mostra no console
    .catch(error => {
        console.error('Erro:', error);
    });
});

// Função para mostrar os filmes recomendados na página
function displayRecommendations(filmes) {
    // Pega o elemento onde os filmes serão mostrados
    const recommendationsDiv = document.getElementById('recommendations');
    // Limpa qualquer coisa que estava lá antes
    recommendationsDiv.innerHTML = '';

    // Se não tiver nenhum filme
    if (filmes.length === 0) {
        // Mostra uma mensagem dizendo que não encontrou nenhum filme
        recommendationsDiv.innerHTML = '<p>Nenhum filme encontrado para as preferências informadas.</p>';
        return;
    }

    // Para cada filme na lista de filmes recebida
    filmes.forEach((filme, index) => {
        // Adiciona as informações do filme no HTML
        recommendationsDiv.innerHTML += `
            <div class="filme">
                <h3>Filme ${index + 1}: ${filme.nome}</h3>
                <p><strong>Ano:</strong> ${filme.ano}</p>
                <p><strong>Duração:</strong> ${filme.duracao} minutos</p>
                <p><strong>Gêneros:</strong> ${filme.generos.join(', ')}</p>
                <a href="${filme.link}" target="_blank">Ver mais</a>
            </div>
        `;
    });
}
