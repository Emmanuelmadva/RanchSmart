from database.connection import engine

try:
    connection = engine.connect()
    print(" Connexion réussie à la base PostgreSQL !")
    connection.close()
except Exception as e:
    print(" Erreur de connexion :", e)
