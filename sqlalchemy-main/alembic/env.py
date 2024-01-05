from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config


fileConfig(config.config_file_name)

from models import Base
target_metadata = Base.metadata

from models import Student, Group, Teacher, Subject, Grade
from alembic import op
target_metadata = [Student.metadata, Group.metadata, Teacher.metadata, Subject.metadata, Grade.metadata]

def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    if context.dialect.name == 'sqlite' and inspected_type == 'FLOAT' and metadata_type == 'REAL':
        return False
    else:
        return None

with engine_from_config(
    config.get_section(config.config_ini_section),
    prefix='sqlalchemy.',
    poolclass=pool.NullPool,
) as engine:
    context.configure(
        connection=engine.connect(),
        target_metadata=target_metadata,
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()