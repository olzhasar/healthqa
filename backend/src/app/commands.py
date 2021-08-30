import click
from flask import Flask
from flask.cli import with_appcontext

import crud
from db.database import db


@click.command("create_user")
@click.option("--email", prompt="Email")
@click.option("--name", prompt="Display name")
@click.option("--password", prompt="Password")
@with_appcontext
def create_user(email: str, name: str, password: str):
    user = crud.user.create_user(db, email=email, name=name, password=password)
    crud.user.mark_email_verified(db, user=user)
    click.echo(f"Created user with id {user.id}")


def init_app(app: Flask):
    app.cli.add_command(create_user)
