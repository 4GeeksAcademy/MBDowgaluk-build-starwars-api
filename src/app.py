"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, Planets, FavouritePlanets, Characters, FavouriteCharacters
from datetime import datetime
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        response_body = {}
        results = {}
        users = db.session.execute(db.select(Users)).scalars()
        list_usuarios = []
        for row in users:
            list_usuarios.append(row.serialize())
        results['users'] = list_usuarios
        # Opcion 2: results['users'] = [row.serialize() for row in users]
        response_body['message'] = 'Listado de usuarios'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'POST':
        response_body = {}
        data = request.json
        user = Users(first_name = data.get('first_name'),
                     last_name = data.get('last_name'),
                     email = data.get('email'),
                     password = data.get('password'),
                     is_active = True,
                     suscription_date = datetime.now()
                     )
        db.session.add(user)
        db.session.commit()
        response_body['user'] = user.serialize()
        return response_body, 200


@app.route('/users/<int:id_user>', methods=['GET','PUT','DELETE'])
def handle_user(id_user):
    if request.method == 'GET':
        response_body = {}
        results = {}
        user = db.session.get(Users, id_user)
        if not user:
            response_body['message'] = 'Usuario inexistente'
            return response_body, 404
        results['user'] = user.serialize()
        response_body['message'] = 'Usuario encontrado'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'PUT':
        response_body = {}
        results = {}
        data = request.json
        user = db.session.execute(db.select(Users).where(Users.id == id_user)).scalar()
        if not user:
            response_body['message'] = 'Usuario inexistente'
            return response_body, 400
        user.email = data.get('email')
        db.session.commit()
        results['user'] = user.serialize()
        response_body['message'] = 'Usuario modificado'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'DELETE':
        response_body = {}
        user = db.session.execute(db.select(Users).where(Users.id == id_user)).scalar()
        if not user:
            response_body['message'] = 'Usuario inexistente'
            return response_body, 400
        db.session.delete(user)
        db.session.commit()
        response_body['message'] = 'Usuario eliminado'
        return response_body, 200


@app.route('/planets', methods=['GET','POST'])
def handle_planets():
    if request.method == 'GET':
        response_body = {}
        results = {}
        planets = db.session.execute(db.select(Planets)).scalars()
        results['planets'] = [row.serialize() for row in planets]
        response_body['message'] = 'Listado de planetas'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'POST':
        response_body = {}
        data = request.json
        planet = Planets(name = data.get('name'),
                        climate = data.get('climate'),
                        diameter = data.get('diameter'),
                        orbital_period = data.get('orbital_period'),
                        population = data.get('population'),
                        rotation_period = data.get('rotation_period'),  
                        terrain = data.get('terrain'))
        db.session.add(planet)
        db.session.commit()
        response_body['planet'] = planet.serialize()
        return response_body, 200


@app.route('/planets/<int:planet_id>', methods=['GET','DELETE'])
def handle_planet(planet_id):
    if request.method == 'GET':
        response_body = {}
        results = {}
        planet = db.session.get(Planets, planet_id)
        if not planet:
            response_body['message']: 'Planeta no encontrado'
            return response_body, 400
        results['planet'] = planet.serialize()
        response_body['message'] = 'Planeta encontrado'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'DELETE':
        response_body = {}
        planet = db.session.execute(db.select(Planets).where(Planets.id == planet_id)).scalar()
        if not planet:
            response_body['message'] = 'Planeta no encontrado'
            return response_body, 400
        db.session.delete(planet)
        db.session.commit()
        response_body['message'] = 'Planeta eliminado'
        return response_body, 200


@app.route('/characters', methods=['GET','POST'])
def handle_characters():
    if request.method == 'GET':
        response_body = {}
        results = {}
        characters = db.session.execute(db.select(Characters)).scalars()
        results['characters'] = [row.serialize() for row in characters]
        response_body['message'] = 'Listado de personajes'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'POST':
        response_body = {}
        data = request.json
        character = Characters(name = data.get('name'),
                               eye_color = data.get('eye_color'),
                               gender = data.get('gender'),
                               mass = data.get('mass'), 
                               skin_color = data.get('skin_color'))
        db.session.add(character)
        db.session.commit()
        response_body['message'] = 'Personaje creado'
        response_body['results'] = character.serialize()
        return response_body, 200


@app.route('/characters/<int:character_id>', methods=['GET','DELETE'])
def handle_character(character_id):
    if request.method == 'GET':
        response_body = {}
        results = {}
        character = db.session.get(Characters, character_id)
        if not character:
            response_body['message'] = 'Personaje no encontrado'
            return response_body, 404
        results['character'] = character.serialize()
        response_body['message'] = 'Personaje encontrado'
        response_body['results'] = results
        return response_body, 200
    if request.method == 'DELETE':
        response_body = {}
        character = db.session.execute(db.select(Characters).where(Characters.id == character_id)).scalar()
        if not character:
            response_body['message'] = 'Personaje no encontrado'
        db.session.delete(character)
        db.session.commit()
        response_body['message'] = 'Personaje eliminado'
        return response_body, 200


@app.route('/users/favourite_planets', methods=['GET'])
def handle_favourite_planets():
    if request.method == 'GET':
        response_body = {}
        results = {}
        favourite_planets = db.session.execute(db.select(FavouritePlanets)).scalars()
        results['favourite_planets'] = [row.serialize() for row in favourite_planets]
        response_body['message'] = 'Listado de planetas favoritos'
        response_body['results'] = results
        return response_body, 200


@app.route('/users/<int:user_id>/favourite_planets/<int:planet_id>', methods=['POST', 'DELETE'])
def handle_favourite_planets_byuser(user_id, planet_id):
    if request.method == 'POST':
        response_body = {}
        user = db.session.get(Users, user_id)
        planet = db.session.get(Planets, planet_id)
        if not user:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400
        if not planet:
            response_body['message'] = 'Planeta no encontrado'
            return response_body, 400
        favourite_planet = FavouritePlanets(user_id = user_id,
                                            planet_id = planet_id)
        db.session.add(favourite_planet)
        db.session.commit()
        response_body['message'] = 'Planeta favorito agregado'
        response_body['results'] = favourite_planet.serialize()
        return response_body, 200
    if request.method == 'DELETE':
        response_body = {}
        planet = db.session.execute(db.select(FavouritePlanets).where(FavouritePlanets.user_id == user_id, FavouritePlanets.planet_id == planet_id)).scalar()
        if not planet:
            response_body['message'] = 'Planeta favorito no encontrado'
            return response_body, 400
        db.session.delete(planet)
        db.session.commit()
        response_body['message'] = 'Planeta favorito eliminado'
        return response_body, 200


@app.route('/users/favourite_characters', methods=['GET'])
def handle_favourite_characters():
    response_body = {}
    results = {}
    favourite_characters = db.session.execute(db.select(FavouriteCharacters)).scalars()
    results['favourite_characters'] = [row.serialize() for row in favourite_characters]
    response_body['message'] = 'Listado de personajes favoritos'
    response_body['results'] = results
    return response_body, 200

@app.route('/users/<int:user_id>/favourite_characters/<int:character_id>', methods=['POST','DELETE'])
def handle_favourite_character_byuser(user_id, character_id):
    if request.method == 'POST':
        response_body = {}
        user = db.session.get(Users, user_id)
        character = db.session.get(Characters, character_id)
        if not user:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400
        if not character:
            response_body['message'] = 'Personaje no encontrado'
            return response_body, 400
        favourite_character = FavouriteCharacters(user_id = user_id,
                                                  character_id = character_id)
        db.session.add(favourite_character)
        db.session.commit()
        response_body['message'] = 'Personaje favorito agregado'
        response_body['results'] = favourite_character.serialize()
        return response_body, 200
    if request.method == 'DELETE':
        response_body = {}
        character = db.session.execute(db.select(FavouriteCharacters).where(FavouriteCharacters.user_id == user_id, FavouriteCharacters.character_id == character_id)).scalar()
        if not character:
            response_body['message'] = 'Personaje favorito no encontrado'
            return response_body, 400
        db.session.delete(character)
        db.session.commit()
        response_body['message'] = 'Personaje favorito eliminado'
        return response_body, 200


@app.route('/users/<int:user_id>/favourites', methods=['GET'])
def favourites_by_user(user_id):
    response_body = {}
    results = {}
    if not user_id:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400
    favourite_planets = db.session.execute(db.select(FavouritePlanets).where(FavouritePlanets.user_id == user_id)).scalars()
    favourite_characters = db.session.execute(db.select(FavouriteCharacters).where(FavouriteCharacters.user_id == user_id)).scalars()
    results['favourite_planets'] = [row.serialize() for row in favourite_planets]
    results['favourite_characters'] = [row.serialize() for row in favourite_characters]
    response_body['message'] = 'Listado de favoritos del usuario'
    response_body['results'] = results
    return response_body, 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
