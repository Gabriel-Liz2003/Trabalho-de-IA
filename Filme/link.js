<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Recomendação de Filmes</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Sistema de Recomendação de Filmes</h1>
    <form id="preferencesForm">
        <label for="genre">Gênero:</label>
        <select id="genre">
            <option value="Ação">Ação</option>
            <option value="Comédia">Comédia</option>
            <option value="Drama">Drama</option>
            <option value="Terror">Terror</option>
            <option value="Animação">Animação</option>
            <!-- Adicione outros gêneros conforme o mapa -->
        </select><br>

        <label for="duration">Duração:</label>
        <select id="duration">
            <option value="Indiferente">Indiferente</option>
            <option value="Longos">Longos</option>
            <option value="Curto">Curto</option>
        </select><br>

        <label for="year">Ano de lançamento:</label>
        <input type="text" id="year" placeholder="Ex: 2020"><br>

        <button type="button" onclick="getRecommendations()">Buscar Filmes</button>
    </form>

    <div id="results"></div>

    <script>
        function getRecommendations() {
            const genre = document.getElementById('genre').value;
            const duration = document.getElementById('duration').value;
            const year = document.getElementById('year').value;

            fetch(/api/recommend?genre=${genre}&duration=${duration}&year=${year})
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.innerHTML = '';

                    if (data.length === 0) {
                        resultsDiv.innerHTML = '<p>Não foi possível encontrar filmes para as preferências informadas.</p>';
                        return;
                    }

                    data.forEach((filme, index) => {
                        const filmeElement = document.createElement('div');
                        filmeElement.innerHTML = 
                            <h2>Filme ${index + 1}: ${filme.nome}</h2>
                            <p><strong>Link:</strong> <a href="${filme.link}" target="_blank">${filme.link}</a></p>
                            <p><strong>Ano:</strong> ${filme.ano}</p>
                            <p><strong>Duração:</strong> ${filme.duracao} minutos</p>
                            <p><strong>Gêneros:</strong> ${filme.generos.join(', ')}</p>
                        ;
                        resultsDiv.appendChild(filmeElement);
                    });
                })
                .catch(error => console.error('Erro ao buscar recomendações:', error));
        }
    </script>
</body>
</html>