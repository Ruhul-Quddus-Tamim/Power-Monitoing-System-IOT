import os
os.environ["FLASK_APP"] = "server.py"
from flask.cli import FlaskGroup

from base import db
from server import app, User


cli = FlaskGroup(app)

ROOT_NAME: str = os.getenv('ROOT_NAME',"root")
ROOT_EMAIL: str = os.getenv('ROOT_EMAIL',"root@mail.com")
ROOT_PASSWORD: str = os.getenv('ROOT_PASSWORD',"root")

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(name=ROOT_NAME, email=ROOT_EMAIL, password=ROOT_PASSWORD, is_admin=True))
    db.session.commit()

if __name__ == "__main__":
    cli()
