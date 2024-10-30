from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for
)
from pymongo import MongoClient
import requests
from datetime import datetime

app = Flask(__name__)

client = MongoClient('mongodb+srv://MuhammadRizkySamuel:123@cluster0.yxozh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if isinstance(definition, str) else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg = request.args.get('msg')
    return render_template(
        'index.html',
        words=words,
        msg=msg
    )


@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = 'e2fdbc6a-2c18-4d7a-b60a-99b0dc2083a2'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    # Jika tidak ada definisi yang ditemukan
    if not definitions:
        return redirect(url_for('error_page', keyword=keyword))

    if isinstance(definitions[0], str):
        # Jika ada saran kata dari API
        suggestions = ', '.join(definitions)
        return redirect(url_for(
            'error_page',
            keyword=keyword,
            suggestions=suggestions
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/error/<keyword>')
def error_page(keyword):
    suggestions = request.args.get('suggestions', '').split(', ')
    return render_template('error.html', keyword=keyword, suggestions=suggestions)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%y%m%d'),
    }

    db.words.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'The word, {word}, was saved!!!',
    })


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'The word {word} was deleted'
    })


@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word: word'})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({'result': 'success'})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    return jsonify({'result': 'success'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)