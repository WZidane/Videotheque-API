from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import psycopg2, os, bcrypt, json, uuid
from psycopg2.extras import RealDictCursor

ACCESS_EXPIRES = timedelta(hours=1)

# Load the .env file
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Initialisation de jwt
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers']

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)

conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')  
    )

@app.route('/api', methods=['GET'])
def index():
    return "Hello, World! cest pas moi la"

@app.route('/api/isconnected', methods=['GET'])
# Test pour voir si un utilisateur est bien connecté avec son token
@jwt_required()
def isConnected():
    try:
        user_id = get_jwt_identity()
        return {"isConnected": True}
    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur. : {e}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    cur = conn.cursor()
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email et mot de passe sont obligatoires."}), 400

        # Récupération du hash de mdp stocké dans la db
        cur.execute('SELECT username, password FROM "User" WHERE email = %s', (email,))
        result = cur.fetchone()

        if not result:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        stored_password = result[1]

        # Vérification du mot de passe et envoi du token si le mdp est bon
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            access_token = create_access_token(identity=result[0])
            return jsonify({'message': 'Login Success', 'access_token': access_token}), 200
        else:
            return jsonify({"error": "Mot de passe incorrect."}), 401
        
    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur. : {e}"}), 500
    
    finally:
        cur.close()

# Endpoint for revoking the current user's access token
@app.route("/api/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)

    try:
        cur = conn.cursor()

        # Insertion du JTI dans la table blacklist_token
        cur.execute(
            "INSERT INTO blacklist_token (jti, created_at) VALUES (%s, %s)",
            (jti, now)
        )

        # Valider la transaction
        conn.commit()

        return jsonify(msg="JWT revoked")

    except Exception as e:
        print(f"Erreur lors de l'accès à la base de données : {e}")
        return jsonify(msg="Erreur lors de la révocation du JWT"), 500

    finally:
        cur.close()

@app.route('/api/user', methods=['POST'])
def createUser():
    try:
        data = request.get_json()

        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validation des données
        if not username or not email or not password:
            return jsonify({"error": "Tous les champs (username, email, password) sont obligatoires."}), 400
        cur = conn.cursor()

        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Encodage en UTF-8 pour stockage
        hashed_password_encoded = hashedPassword.decode('utf-8')

        query = '''
        INSERT INTO "User" (username, email, password, id_role) 
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        '''

        cur.execute(query, (username, email, hashed_password_encoded, 2))

        conn.commit()

        # Succès
        return jsonify({"message": "Utilisateur créé avec succès."}), 201


    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

    finally: 
        cur.close()

@app.route('/api/user/<int:id_user>', methods=['DELETE'])
def deleteUser(id_user):
    try:
        cur = conn.cursor()

        delete_query = 'DELETE FROM "User" WHERE id = %s'

        cur.execute(
            delete_query, 
            (id_user,)
            )

        conn.commit()

        if cur.rowcount > 0:
            return jsonify({"message": f"L'utilisateur avec l'ID {id_user} a été supprimé."}), 200
        else:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

    finally:
        cur.close()

        
@app.route('/api/users/<int:page>', methods=['GET'])
def getUsersByPage(page):
    
    cur = conn.cursor()

    cur.execute(
        'SELECT u.id, u.username, u.email, r.name FROM "User" u JOIN "Role" r on r.id = u.id_role ORDER BY u.id LIMIT 50 OFFSET %s', 
        ((page-1)*50,)
        )

    results = cur.fetchall()

    cur.close()

    return results, 200

# Fonction appelée lors d'un @jwt_required(), sert à vérifier si un token est blacklist ou non
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jti = uuid.UUID(jwt_payload["jti"])
    cur = conn.cursor()
    try:
        cur.execute('SELECT id FROM "blacklist_token" WHERE jti=%s', (str(jti),))
        token = cur.fetchone()

        # Retourne True si le token est blacklist
        return token is not None
    except Exception as e:
        return jsonify({"error": "Il y a eu une erreur interne du serveur"}), 500
    finally:
        cur.close()
        
@app.route('/api/users', methods=['GET'])
def getUsers():
    try:
        cur = conn.cursor()

        cur.execute('SELECT * FROM "User"')

        result = cur.fetchall()

        cles = ["id", "username", "email", "password", "id_role"]

        table = [] 
        for sous_liste in result:
            objet = {}
            for index, valeur in enumerate(sous_liste):
                objet[cles[index]] = valeur
            table.append(objet)

        res = {}

        res['Users'] = table

        return res

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

    finally:
        cur.close()

@app.route('/api/movies', methods=['GET'])
def getMovies():
    try:
        cur = conn.cursor()

        cur.execute('SELECT * FROM "Movie"')

        result = cur.fetchall()

        cles = ["id", "id_imdb", "title", "country", "director", "synopsis", "duration", "poster", "release_date"]

        table = [] 
        for sous_liste in result:
            objet = {}
            for index, valeur in enumerate(sous_liste):
                objet[cles[index]] = valeur
            table.append(objet)

        res = {}

        res['Movies'] = table

        return res

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

    finally:
        cur.close()

@app.route('/api/movie/<id>', methods=['GET'])
def getMovie(id):
    try:

        cur = conn.cursor()

        cur.execute('SELECT * FROM "Movie" WHERE id_tmdb = %s', (id,))

        result = cur.fetchall()

        cles = ["id", "id_tmdb", "title_fr", "title_en", "country", "release_date", "synopsis_fr", "synopsis_en", "poster"]

        table = [] 
        for sous_liste in result:
            objet = {}
            for index, valeur in enumerate(sous_liste):
                objet[cles[index]] = valeur
            table.append(objet)

        res = {}

        res['Movie'] = table

        if(result):
            return res
        else:
            return jsonify({'error': 404});

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

    finally:
        cur.close()

@app.route('/api/movie/', methods=['POST'])
def createMovie():
    try:

        data = request.get_json()

        id_tmdb = data.get('id')
        title_fr = data.get('title_fr')
        title_en = data.get('title_en')
        country = data.get('country')
        release_date = data.get('release_date')
        synopsis_fr = data.get('synopsis_fr')
        synopsis_en = data.get('synopsis_en')
        poster = data.get('poster')
        

        if not id_tmdb or not title_fr or not title_en or not country or not synopsis_fr or not synopsis_en or not poster or not release_date:
            return jsonify({"error": "Tous les champs sont obligatoires."}), 400
        
        cur = conn.cursor()

        cur.execute('INSERT INTO "Movie" (id_tmdb, title_fr, title_en, country, synopsis_fr, synopsis_en, poster, release_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (id_tmdb, title_fr, title_en, country, synopsis_fr, synopsis_en, poster, release_date))

        conn.commit()
        
        return jsonify({"message": "Film créé avec succès."}), 201

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500


@app.route('/api/isconnected', methods=['GET'])
# Test pour voir si un utilisateur est bien connecté avec son token
@jwt_required()
def isConnected():
    try:
        return jsonify({"isConnected": True}), 200
    except Exception as e:
        return jsonify({"isConnected": f"Erreur interne du serveur. : {e}"}), 500
    finally:
        cur.close()
    
@app.route('/api/collection/<id>', methods=['POST'])
@jwt_required()
def addToCollection(id):
    username = get_jwt_identity()

    try: 
        cur = conn.cursor()
        cur.execute('SELECT id FROM "User" WHERE username=%s',(username,))
        user_id = cur.fetchone()
        if(user_id):
            cur.execute('SELECT id FROM "Movie" WHERE id_tmdb=%s', (id,))
            movie_id = cur.fetchone()
            if(movie_id):
                cur.execute('INSERT INTO "Videotheque" ("user_id", "movie_id") VALUES (%s, %s);', (user_id, movie_id))
                conn.commit()

                return jsonify({"message": "Le film a été ajouté à la collection"}), 201
            return jsonify({"error": "Le film n'existe pas dans la bdd"}), 404
        return jsonify({"error": "L'utilisateur n'existe pas"}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500
    finally:
        cur.close()

@app.route('/api/collection', methods=['GET'])
@jwt_required()
def getCollection():
    username = get_jwt_identity()
    data = request.get_json()
    language = data.get("language")
    
    if language:
        title = f"title_{language}"
        synopsis = f"title_{language}"
    else:
        title = "title_fr"
        synopsis = "synopsis_fr"

    cur = None
    try: 
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM "User" WHERE username=%s',(username,))
        user = cur.fetchone()
        cur.close()
        if(user):
            cur = conn.cursor(cursor_factory=RealDictCursor)
            query = f'SELECT m.id, m.id_tmdb, m.{title}, m.{synopsis}, m.poster FROM "Videotheque" v INNER JOIN "Movie" m ON v.movie_id = m.id WHERE user_id=%s'
            cur.execute(query, (user[0],))
            results = cur.fetchall()
            return jsonify({"user": user, "movies": results}), 200
        return jsonify({"error": "L'utilisateur n'existe pas"}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500
    finally:
        if cur:
            cur.close()

@app.route('/api/collection/<id>', methods=['DELETE'])
@jwt_required()
def removeFromCollection(id):
    username = get_jwt_identity()

    try: 
        cur = conn.cursor()
        cur.execute('SELECT id FROM "User" WHERE username=%s',(username,))
        user_id = cur.fetchone()
        if(user_id):
            cur.execute('SELECT v.id FROM "Videotheque" v INNER JOIN "Movie" m ON v.movie_id=m.id WHERE m.id_tmdb=%s AND v.user_id=%s', (id,user_id,))
            v_id = cur.fetchone()
            if(v_id):
                cur.execute('DELETE FROM "Videotheque" WHERE (("id" = %s));', (v_id,))
                conn.commit()

                return jsonify({"message": "Le film a été supprimé de la collection"}), 200
            return jsonify({"error": "Ce film n'est pas dans votre collection"}), 400
        return jsonify({"error": "L'utilisateur n'existe pas"}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500
    finally:
        cur.close()

@app.route('/api/collection/<id>', methods=['GET'])
@jwt_required()
def isInCollection(id):
    username = get_jwt_identity()

    try:
        cur = conn.cursor()
        cur.execute('SELECT id FROM "User" WHERE username=%s',(username,))
        user_id = cur.fetchone()
        if user_id:
            cur.execute('SELECT v.id FROM "Videotheque" v INNER JOIN "Movie" m ON v.movie_id=m.id WHERE m.id_tmdb=%s AND v.user_id=%s', (id,user_id,))
            v_id = cur.fetchone()
            if v_id:
                return jsonify({'isInCollection': True}), 200
            return jsonify({'isInCollection': False}), 200
    except Exception as e:
        return jsonify({"error": "Erreur interne du serveur"}), 500
    finally:
        cur.close()