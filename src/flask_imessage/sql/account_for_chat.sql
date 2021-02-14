-- The most recent account id per chat id.
-- Used to send messages to the relevant account. Is probs a hack but here i am.
-- 
-- User needs to .format(chatId-...)

select chat.account_id

from chat
join chat_message_join on chat.rowid = chat_message_join.chat_id

where chat.chat_identifier = '{chat_id}'

order by chat_message_join.message_id desc
limit 1
