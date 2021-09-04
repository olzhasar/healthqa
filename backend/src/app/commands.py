import click
from flask import Flask
from flask.cli import with_appcontext

import repository as repo
from storage import store


@click.command("create_user")
@click.option("--email", prompt="Email")
@click.option("--name", prompt="Display name")
@click.option("--password", prompt="Password")
@with_appcontext
def create_user(email: str, name: str, password: str):
    user = repo.user.create(store.db, email=email, name=name, password=password)
    repo.user.mark_email_verified(store, user)
    click.echo(f"Created user with id {user.id}")


def init_app(app: Flask):
    app.cli.add_command(create_user)
