"""Handlers for the database."""
import itertools
import sqlite3
import typing

from . import config


class InvalidServiceError(Exception):
    """Raised when no account ID can be located for a chat."""

    pass


def query(sql: str) -> typing.List[typing.Dict[str, typing.Any]]:
    """Run a SQL query in the chat DB.

    Return a list of dicts with one key per column of the data.
    """

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    with sqlite3.connect(config.DB_PATH) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()

    return result


def get_account_for_chat(chat_id: str) -> str:
    """Run account_for_chat.sql to return the latest account id for a chat."""
    sql = (
        (config.WHEREAMI / "sql/account_for_chat.sql")
        .read_text()
        .format(chat_id=chat_id)
    )
    data = query(sql)

    try:
        return data[0]["account_id"]
    except IndexError:
        raise InvalidServiceError(f"Unknown service for chat: {chat_id}")


def get_flat_messages(where: str = None) -> typing.List[dict]:
    """Run the messages_flat.sql file to return all messages.

    Option to insert a WHERE clause.
    """
    sql = (config.WHEREAMI / "sql/messages_flat.sql").read_text()

    if where is not None:
        sql += "\nwhere " + where

    return query(sql)


def group_flat_messages(
    messages_flat: typing.List[dict], by: str = "chat_id"
) -> typing.Dict[str, list]:
    """Group messages (as returned by get_flat) by a key.

    This is a helper to provide data in a structure expected around the app.
    """
    grouped = dict()
    for key, group in itertools.groupby(
        sorted(messages_flat, key=lambda x: x[by]),
        lambda x: x[by].strip(),
    ):
        grouped[key] = list(group)
    return grouped
