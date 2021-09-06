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
def create_user(email: str, name: str, password: str) -> None:
    user = repo.user.create(store, email=email, name=name, password=password)
    repo.user.mark_email_verified(store, user)
    click.echo(f"Created user with id {user.id}")


@click.command("update_search_indexes")
@with_appcontext
def update_search_indexes() -> None:
    questions = repo.question.all(store)
    repo.question.update_search_indexes(store, *questions)


@click.command("configure_search_indexes")
@with_appcontext
def configure_search_indexes() -> None:
    questions_index = store.meili.index("question")
    questions_index.update_settings(
        {
            "searchableAttributes": ["title", "content"],
            "displayedAttributes": ["id", "title", "url"],
        }
    )


def init_app(app: Flask) -> None:
    app.cli.add_command(create_user)
    app.cli.add_command(update_search_indexes)
    app.cli.add_command(configure_search_indexes)
