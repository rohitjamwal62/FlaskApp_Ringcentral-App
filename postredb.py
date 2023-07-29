import psycopg2,configparser,time
config = configparser.ConfigParser()

def create_connection():
    try:
        config.read('database.ini')
        connection = psycopg2.connect(
            host = config.get('postgresql', 'host'),
            database = config.get('postgresql', 'database'),
            user = config.get('postgresql', 'user'),
            port = config.get('postgresql', 'port'),
            password = "%dtJkejudi#$3WcVUHK5"
        )
        return connection
    except psycopg2.Error as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None
