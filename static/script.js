document.getElementById('preferencesForm').addEventListener('submit', function (event) {
    event.preventDefault();

    // Pega os valores dos campos do formulário
    const genero = document.getElementById('genero').value;
    const duracao = document.getElementById('duracao').value;
    const ano = document.getElementById('ano').value;

    // Envia os dados via POST para o servidor
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ genero, duracao, ano })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Erro desconhecido');
                });
            }
            return response.json();
        })
        .then(data => {
            displayRecommendations(data);
        })
        .catch(error => {
            console.error('Erro:', error);
            alert("Houve um problema: ${error.message}");
        });
});

// Função para mostrar os filmes recomendados na página
function displayRecommendations(filmes) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = ''; // Limpa qualquer conteúdo anterior

    // Se não houver filmes
    if (!Array.isArray(filmes) || filmes.length === 0) {
        recommendationsDiv.innerHTML = '<p>Nenhum filme encontrado para as preferências informadas.</p>';
        return;
    }

    // Exibe os filmes recomendados
filmes.forEach((filme, index) => {
    // Inicializa a variável para os comentários
    let comentariosHTML = '';

    // Verifica se o filme tem comentários e os exibe
    if (filme.comentarios && filme.comentarios.length > 0) {
        comentariosHTML = `<p><strong>Comentários:</strong><ul>`;
        filme.comentarios.forEach(comentario => {
            comentariosHTML += `<li style="margin-bottom: 8px;">${comentario}</li>`;
        });
        comentariosHTML += '</ul></p>';
    } else {
        comentariosHTML = '<p><strong>Comentários:</strong> Nenhum comentário encontrado.</p>';
    }

    // Cria o HTML para exibir o filme
    recommendationsDiv.innerHTML += `
        <div class="filme">
            <h3>Filme ${index + 1}: ${filme.nome}</h3>
            <!-- Imagem do filme -->
            <img src="${filme.imagem}" alt="${filme.nome}" class="filme-imagem" />

            <!-- Detalhes do filme -->
            <p><strong>Ano:</strong> ${filme.ano || 'não informado'}</p>
            <p><strong>Duração:</strong> ${filme.duracao} minutos</p>
            <p><strong>Gêneros:</strong> ${Array.isArray(filme.generos) ? filme.generos.join(', ') : filme.generos}</p>
            <p><strong>Sinopse:</strong> ${filme.sinopse}</p>

            <!-- Comentários -->
            ${comentariosHTML}

            <!-- Link para ver mais -->
            <a href="${filme.url}" target="_blank" class="ver-mais-btn">Ver mais</a>
        </div>
    `;
});
}