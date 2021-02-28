"""Handlers for the database."""
import itertools
import sqlite3
import typing

from . import apple, config


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


def get_flat_messages(where: str = None) -> typing.List[dict]:
    """Run the messages_flat.sql file to return all messages.

    Option to insert a WHERE clause.
    """
    sql = (config.WHEREAMI / "sql/messages_flat.sql").read_text()

    if where is not None:
        sql += "\nwhere " + where

    messages = query(sql)

    if not messages:
        return messages

    # to later enrich sender names
    phone_number_map = {
        apple.sanitize_phone(contact["phone"]): contact["name"]
        for contact in apple.parse_contacts_tsv()
    }

    # clean stuff outside the SQL
    for message in messages:

        # the chat ID is going to be a comma delimited list of distinct senders.
        # clean it + make a new ID.
        numbers = sorted(
            [apple.sanitize_phone(v) for v in message["chat_id"].split(",")]
        )
        message["chat_id"] = ",".join(numbers)

        # sanitize/enrich the sender id if defined
        if message["sender_id"]:
            message["sender_id"] = apple.sanitize_phone(message["sender_id"])
            message["sender_name"] = phone_number_map.get(message["sender_id"])

        # cast sql int to boolean
        message["is_from_me"] = message["is_from_me"] == 1

    return messages


def group_flat_messages(
    messages_flat: typing.List[dict], byfunc: callable = None
) -> typing.Dict[str, list]:
    """Group messages (as returned by get_flat) by a key.

    This is a helper to provide data in a structure expected around the app.
    """

    def _byfunc(x):
        return x["chat_id"]

    byfunc = byfunc if byfunc is not None else _byfunc

    grouped = dict()
    for key, group in itertools.groupby(sorted(messages_flat, key=byfunc), byfunc):
        grouped[key] = list(group)
    return grouped
