-- UI automation to click the "Sync Now" preferences button of the Messages app.
-- 
-- This will open the messages app, open its preferences via menu click, then navigate
-- to the iMessage preferences and click abutton titled "Sync Now". If ANYTHING
-- changes on apple's end, this will break.

tell application "Messages" to activate
tell application "System Events"
	repeat until visible of process "Messages" is true
	end repeat
end tell


tell application "System Events"
	tell process "Messages"
		tell menu bar 1
			click menu item "Preferences…" of menu "Messages"
		end tell

        delay 1
		
		tell window 1
			tell group 1
				tell tab group 1
					click button "Sync Now"
				end tell
			end tell
		end tell

        delay 1

		-- close preferences
        tell menu bar 1
			click menu item "Close Window" of menu "File"
		end tell

		-- close messages
		tell menu bar 1
			click menu item "Close Window" of menu "File"
		end tell
	end tell
end tell

return 
