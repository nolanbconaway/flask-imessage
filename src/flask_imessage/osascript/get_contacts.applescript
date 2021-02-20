-- Return a list of contact name, phone tuples to be later processed by Python.
--
-- Will return one record per phone number in the Contacts app. Each row will contain:
--  - The common identifier for the contact object
--  - The name of the contact
--  - The phone number
--
-- Output is formatted as a TSV. It might contain a leading and trailing " character.
-- It is slow and I hate it.


set csv to ""

tell application "Contacts"
	repeat with thePerson in people
		repeat with thePhone in phones of thePerson
			set csv to csv & id of thePerson & "\t" & name of thePerson & "\t" & value of thePhone & "\n"
		end repeat
	end repeat
end tell

return csv