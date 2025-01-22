from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2, os, bcrypt, json

# Load the .env file
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

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

@app.route('/test/login', methods=['POST'])
def test():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email et mot de passe sont obligatoires."}), 400
        
        cur = conn.cursor()

        # Récupération du hash de mdp stocké dans la db
        cur.execute('SELECT password FROM "User" WHERE email = %s', (email,))
        result = cur.fetchone()

        if not result:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        stored_password = result[0]

        # Vérification du mot de passe
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({"message": "Connexion réussie."}), 200
        else:
            return jsonify({"error": "Mot de passe incorrect."}), 401
        
    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"error": "Erreur interne du serveur."}), 500
    
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

@app.route('/api/user', methods=['POST'])
def createUser():
    try:

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

        cur.execute(query, (username, email, hashed_password_encoded, 1))

        conn.commit()

        # Succès
        return jsonify({"message": "Utilisateur créé avec succès."}), 201


    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"error": "Erreur interne du serveur."}), 500

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

        # Vérifie si un utilisateur a été supprimé
        if cur.rowcount > 0:
            return jsonify({"message": f"L'utilisateur avec l'ID {id_user} a été supprimé."}), 200
        else:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500

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

        cles = ["id", "id_tmdb", "title", "country", "director", "synopsis", "duration", "poster", "release_date"]

        table = [] 
        for sous_liste in result:
            objet = {}
            for index, valeur in enumerate(sous_liste):
                objet[cles[index]] = valeur
            table.append(objet)

        res = {}

        res['Movie'] = table

        if(res['Movie']):
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
        title = data.get('title')
        country = data.get('country')
        synopsis = data.get('synopsis')
        poster = data.get('poster')
        release_date = data.get('release_date')

        if not id_tmdb or not title or not country or not synopsis or not poster or not release_date:
            return jsonify({"error": "Tous les champs sont obligatoires."}), 400
        
        cur = conn.cursor()

        cur.execute('INSERT INTO "Movie" (id_tmdb, title, country, director, synopsis, duration, poster, release_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (id_tmdb, title, country, "Moi", synopsis, 20, poster, release_date))

        conn.commit()
        
        return jsonify({"message": "Film créé avec succès."}), 201

    except Exception as e:
        print(f"erreur : {e}")
        return jsonify({"error": f"Erreur interne du serveur : {e}"}), 500