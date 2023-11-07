from flask import Flask, render_template, request, jsonify, session
from flask_session import Session 
import os
import random
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)
logging.basicConfig(level=logging.INFO)

# The Pokemon class
class Pokemon:
    def __init__(self, name, types, moves, stats):
        self.name = name
        self.types = types
        self.moves = moves
        self.stats = stats
        self.hp = 100  # Each Pokemon starts with a HP of 100 for this example

    def fight(self, opponent, move):
        # Simplified fight logic
        damage = self.stats['ATTACK'] * random.uniform(0.5, 1.5)
        opponent.hp -= damage
        opponent.hp = max(opponent.hp, 0)  # Prevent negative HP
        result = {
            'move': move,
            'damage': damage,
            'opponent_hp': opponent.hp
        }
        return result

# Placeholder for Pokemon data
pokemons = {
    'Charizard': Pokemon('Charizard', ['Fire'], ['Flamethrower', 'Fly', 'Blast Burn', 'Fire Punch'], {'ATTACK': 12, 'DEFENSE': 8}),
    'Blastoise': Pokemon('Blastoise', ['Water'], ['Water Gun', 'Bubblebeam', 'Hydro Pump', 'Surf'], {'ATTACK': 10, 'DEFENSE': 10}),
    # ... add more Pokemon as needed ...
}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_battle', methods=['POST'])
def start_battle():
    data = request.form
    session['player_pokemon_name'] = data.get('player_pokemon')
    session['opponent_pokemon_name'] = data.get('opponent_pokemon')

    session['player_pokemon'] = {'name': session['player_pokemon_name'], 'hp': 100}
    session['opponent_pokemon'] = {'name': session['opponent_pokemon_name'], 'hp': 100}

    return jsonify({'status': 'Battle started', 'data': session['player_pokemon'], 'opponent': session['opponent_pokemon']}), 200

@app.route('/get_moves/<pokemon_name>')
def get_moves(pokemon_name):
    pokemon = pokemons.get(pokemon_name)
    if pokemon:
        moves = pokemon.moves
        return jsonify(moves), 200
    else:
        return jsonify({"error": "Pokemon not found"}), 404


@app.route('/perform_move', methods=['POST'])
def perform_move():
    data = request.form
    move = data.get('move')
    player_pokemon = pokemons[session['player_pokemon']['name']]
    opponent_pokemon = pokemons[session['opponent_pokemon']['name']]

    if move not in player_pokemon.moves:
        return jsonify({'status': 'Invalid move'}), 400

    # Handle the player's move
    delay_print(f"{player_pokemon.name} used {move}!")
    result = player_pokemon.fight(opponent_pokemon, move)

    # Check for battle end conditions
    if opponent_pokemon.bars <= 0:
        delay_print(f"\n{opponent_pokemon.name} fainted!")
        return jsonify({'status': 'Battle won', 'result': result}), 200

    # Handle the opponent's move
    opponent_move = random.choice(opponent_pokemon.moves)
    delay_print(f"{opponent_pokemon.name} used {opponent_move}!")
    opponent_result = opponent_pokemon.fight(player_pokemon, opponent_move)

    if player_pokemon.bars <= 0:
        delay_print(f"\n{player_pokemon.name} fainted!")
        return jsonify({'status': 'Battle lost', 'result': result}), 200

    # If battle continues
    return jsonify({
        'status': 'Turn completed',
        'player_move': move,
        'player_result': result,
        'opponent_move': opponent_move,
        'opponent_result': opponent_result
    }), 200
    
@app.route('/get_battle_result')
def get_battle_result():
    # Assuming 'battle_logs' is a list stored in session that contains the battle log messages
    battle_logs = session.get('battle_logs', [])
    player_pokemon = session.get('player_pokemon', {'hp': 100})
    opponent_pokemon = session.get('opponent_pokemon', {'hp': 100})

    return jsonify({
        'player': {
            'name': session.get('player_pokemon_name', 'Unknown'),
            'hp': player_pokemon['hp'],
            'hp_percentage': (player_pokemon['hp'] / 100.0) * 100
        },
        'opponent': {
            'name': session.get('opponent_pokemon_name', 'Unknown'),
            'hp': opponent_pokemon['hp'],
            'hp_percentage': (opponent_pokemon['hp'] / 100.0) * 100
        },
        'logs': battle_logs
    }), 200

@app.route('/result')
def result():
    return render_template('result.html')


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'The requested URL was not found on the server.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
