document.getElementById('preferencesForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const genero = document.getElementById('genero').value;
    const duracao = document.getElementById('duracao').value;
    const ano = document.getElementById('ano').value;

    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ genero, duracao, ano })
    })
    .then(response => response.json())
    .then(data => {
        displayRecommendations(data);
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});

function displayRecommendations(filmes) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '';

    if (filmes.length === 0) {
        recommendationsDiv.innerHTML = '<p>Nenhum filme encontrado para as preferências informadas.</p>';
        return;
    }

    filmes.forEach((filme, index) => {
        recommendationsDiv.innerHTML += `
            <div class="filme">
                <h3>Filme ${index + 1}: ${filme.nome}</h3>
                <p><strong>Ano:</strong> ${filme.ano}</p>
                <p><strong>Duração:</strong> ${filme.duracao} minutos</p>
                <p><strong>Gêneros:</strong> ${filme.generos.join(', ')}</p>
                <a href="${filme.link}" target="_blank">Ver mais </a>
            </div>
        `;
    });
}