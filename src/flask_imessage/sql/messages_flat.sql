-- a flat view of all messages
-- 978307200 is 00:00:00 UTC on Jan 1 2001. Apple times dates relative to that stamp.
with messages as (
    select
        message.ROWID as message_id,
        message.date / 1000000000 + 978307200 as date_unix,
        message.text as message_text,
        message.is_from_me,
        chat.chat_identifier as chat_id,
        case when not message.is_from_me then handle.id end as sender_id

    from chat
    join chat_message_join on chat."ROWID" = chat_message_join.chat_id
    join message on chat_message_join.message_id = message."ROWID"
    join handle on message.handle_id = handle."ROWID"
)

select
    message_id,
    chat_id,
    sender_id,
    date_unix,
    is_from_me,
    message_text

from messages
