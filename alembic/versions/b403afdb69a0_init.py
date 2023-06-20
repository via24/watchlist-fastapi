"""init

Revision ID: b403afdb69a0
Revises:
Create Date: 2023-06-19 13:22:36.392704

"""
import os
import re
import bcrypt
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b403afdb69a0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    username = os.getenv("USERNAME", "用户名")
    email = os.getenv("EMAIL", "example@123.com")
    password = os.getenv("PSWD", "123456")

    if not re.search(
        r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,'
        r"3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$",
        email,
    ):
        raise Exception("不正确的email")

    # ### commands auto generated by Alembic - please adjust! ###
    movie = op.create_table(
        "movie",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=60), nullable=False),
        sa.Column("year", sa.String(length=4), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    user = op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        movie,
        [
            {"title": "My Neighbor Totoro", "year": "1988"},
            {"title": "Dead Poets Society", "year": "1989"},
            {"title": "A Perfect World", "year": "1993"},
            {"title": "Leon", "year": "1994"},
            {"title": "Mahjong", "year": "1996"},
            {"title": "Swallowtail Butterfly", "year": "1996"},
            {"title": "King of Comedy", "year": "1999"},
            {"title": "Devils on the Doorstep", "year": "1999"},
            {"title": "WALL-E", "year": "2008"},
            {"title": "The Pork of Music", "year": "2012"},
        ],
    )
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(13))
    op.bulk_insert(
        user,
        [{"name": username, "email": email, "hashed_password": pwd.decode()}],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    op.drop_table("movie")
    # ### end Alembic commands ###
