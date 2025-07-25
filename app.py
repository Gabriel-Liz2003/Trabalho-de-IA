from flask import Flask, jsonify, request, render_template

from Filme import criar_crawler_adorocinema, criar_crawler_tmdb

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def get_data():
    data = {'key': 'value'}
    return jsonify(data)


@app.route('/recommend', methods=['POST'])
def recommend():
    preferences = request.json
    if not preferences:
        return jsonify({"error": "No preferences provided"}), 400

    genero = preferences.get('genero', '')
    duracao = preferences.get('duracao', '')
    ano = preferences.get('ano', '')
    fonte = preferences.get('fonte', 'adorocinema')

    # Executa o crawler
    if fonte == 'tmdb':
        filmes_recomendados = criar_crawler_tmdb(genero, duracao, ano)
    else:
        filmes_recomendados = criar_crawler_adorocinema(genero, duracao, ano)

    if not filmes_recomendados:
        return jsonify({"error": "No recommendations found"}), 404

    return jsonify(filmes_recomendados), 200


if __name__ == '__main__':
    app.run(debug=True)
