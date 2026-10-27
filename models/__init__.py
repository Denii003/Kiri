# Importar todos los modelos aquí garantiza que SQLModel conozca todas las tablas
# y sus relaciones antes de crear el esquema.
from models.user_model import Usuario  # noqa: F401
from models.Refrigerador_model import Refrigerador  # noqa: F401
from models.Alimento_model import Alimento  # noqa: F401
