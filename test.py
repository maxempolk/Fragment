# mysql+pymysql://root:1234@localhost:3306//FRAGMENT

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Проверьте двойной слеш в URL
connection_string = "mysql+pymysql://root:1234@localhost:3306/FRAGMENT"
# Было: mysql+pymysql://root:1234@localhost:3306//FRAGMENT

try:
    engine = create_engine(connection_string)
    connection = engine.connect()
    print("Подключение успешно!")
    connection.close()
except SQLAlchemyError as e:
    print(f"Ошибка SQLAlchemy: {e}")
