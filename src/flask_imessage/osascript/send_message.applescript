on run {targetBuddyPhone, targetMessage, targetService}
    tell application "Messages"
		set targetBuddy to participant targetBuddyPhone of service id targetService
		send targetMessage to targetBuddy
    end tell
end run