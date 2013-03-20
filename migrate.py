from alembic.config import Config
from alembic import command

def migrate(version="head"):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, version)
    
if __name__ == "__main__":
    import appconfig as conf
    migrate(conf.ALEMBIC_VERSION)