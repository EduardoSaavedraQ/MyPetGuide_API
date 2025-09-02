from utils.helpers import get_engine
from sqlmodel import text
from sqlalchemy.exc import TimeoutError, StatementError, SQLAlchemyError
import toml
from typing import Any
from dotenv import load_dotenv
import sys
from pathlib import Path

opts: list[str] = [opt for opt in sys.argv[1:] if opt.startswith('--') or opt.startswith('-')]
excluded_seeders: list[str] = []
only_seeders: list[str] = []

for opt in opts:
    if opt not in ['--help', '-h', '--exclude', '-e', '--only', '-o']:
        print(f"Error: Opción no reconocida '{opt}'")
        print("Usa --help o -h para ver las opciones disponibles.")
        sys.exit(1)

if ('--exclude' in opts or '-e' in opts) and ('--only' in opts or '-o' in opts):
    print("Error: No se pueden usar las opciones --exclude (-e) y --only (-o) juntas.")
    print("Usa --help o -h para ver las opciones disponibles.")
    sys.exit(1)

if '--help' in opts or '-h' in opts:
    print("Uso: python supabase_remote_seeder.py [opciones]")
    print("Opciones:")
    print("  --help, -h       Muestra esta ayuda y sale")
    print("  --exclude, -e <seeder1, seeder2, ...>  Excluye los seeders (sin extensión .sql) especificados (separados por comas) de la ejecución. No debe especificarse junto con --only o -o")
    print("  --only, -o <seeder1, seeder2, ...>     Ejecuta solo los seeders (sin extension .sql) especificados (separados por comas)")
    print("Si no se especifica ninguna opción, se ejecutan todos los seeders definidos en el archivo de configuración de Supabase.")
    sys.exit(0)

if '--exclude' in opts or '-e' in opts:
    try:
        excluded_seeders = sys.argv[sys.argv.index('--exclude') + 1].split(',')
    except (IndexError):
        print("Error: Debe especificar al menos un seeder para excluir después de la opción --exclude o -e.")
        sys.exit(1)
    except ValueError:
        excluded_seeders: list[str] = sys.argv[sys.argv.index('-e') + 1].split(',')

if '--only' in opts or '-o' in opts:
    try:
        only_seeders = sys.argv[sys.argv.index('--only') + 1].split(',')
    except (IndexError):
        print("Error: Debe especificar al menos un seeder para ejecutar después de la opción --only o -o.")
        sys.exit(1)
    except ValueError:
        only_seeders = sys.argv[sys.argv.index('-o') + 1].split(',')

def ejecutar_seeders_especificados():
    for seeder in only_seeders:
        with open(f"./supabase/seeds/{seeder}.sql", 'r', encoding='UTF-8') as seeder_file:
            print(f"Ejecutando seeder: ./supabase/{seeder}.sql")
            sql_commands = seeder_file.read()
            conn.execute(text(sql_commands))

def ejecutar_seeders_no_excluidos():
    with open("./supabase/config.toml", 'r') as config_file:
        config: dict[str: Any] = toml.load(config_file)

        paths_seeders: list[str]  = config['db']['seed']['sql_paths']

        for path in paths_seeders:
            path = path.replace('\\', '/') # Reemplaza '\' por '/' para compatibilidad entre sistemas operativos'
            path = path.lstrip('./') # Elimina './' del inicio de la ruta si está presente

            if Path(path).stem not in excluded_seeders:
                with open(f"./supabase/{path}", 'r', encoding='UTF-8') as seeder_file:
                    print(f"Ejecutando seeder: ./supabase/{path}")
                    sql_commands = seeder_file.read()
                    conn.execute(text(sql_commands))

try:
    load_dotenv()
    with get_engine().connect() as conn:
        if '--only' in opts or '-o' in opts:
                ejecutar_seeders_especificados()
        else:
            ejecutar_seeders_no_excluidos()
        conn.commit()

    print("La base de datos ha sido inicializada correctamente.")

except FileNotFoundError as e:
    print("No se ha encontrado el archivo de configuración o uno de los archivos SQL especificados en éste. Error:", e)

except TimeoutError as e:
    print("Se ha producido un error de tiempo de espera al intentar conectar con la base de datos.")
    print("Detalles del error:", e)

except StatementError as e:
    print("Se ha producido un error al ejecutar una sentencia SQL.")
    print("Detalles del error:", e)

except SQLAlchemyError as e:
    print("Se ha producido un error relacionado con SQLAlchemy.")
    print("Detalles del error:", e)

except Exception as e:
    print("Se ha producido un error inesperado")
    print("Detalles del error:", e)


