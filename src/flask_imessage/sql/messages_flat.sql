-- a flat view of all messages
-- 978307200 is 00:00:00 UTC on Jan 1 2001, Apple dates relative to that stamp.

with my_handles as (
    select distinct handle.id
    from message
    join handle on message.handle_id = handle."ROWID"
    where message.is_from_me = 1
),

participants as (
    select
        chat_handle_join.chat_id as chat_rowid,
        group_concat(handle.id, ',') as participants_list
    from chat_handle_join
    join handle on chat_handle_join.handle_id = handle."ROWID"
    where handle."ROWID" not in (select * from my_handles)
    group by 1
),

messages as (
    select
        participants.participants_list as chat_id,
        message."ROWID" as message_id,
        message.date / 1000000000 + 978307200 as date_unix,
        message.text as "message_text",
        message.is_from_me,
        case when not message.is_from_me then handle.id end as sender_id,
        message.account_guid as account_guid

    from chat
    join chat_message_join on chat."ROWID" = chat_message_join.chat_id
    join message on chat_message_join.message_id = message."ROWID"
    join handle on message.handle_id = handle."ROWID"
    join participants on participants.chat_rowid = chat."ROWID"

    order by message.date desc
)

select
    message_id,
    chat_id,
    sender_id,
    date_unix,
    is_from_me,
    message_text,
    account_guid

from messages
