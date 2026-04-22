from sqlalchemy import create_engine, text
from config import settings

def test_connection():
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Conexion exitosa")
            print(f"PostgreSQL: {version}")

            tables = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            print(f"\nTablas encontradas:")
            for row in tables:
                print(f"  - {row[0]}")

    except Exception as e:
        print(f"Error de conexion: {e}")

if __name__ == '__main__':
    test_connection()