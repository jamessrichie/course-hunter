on setupSafari()
    tell application "System Events"
        tell application "Safari" to quit saving no
        delay 1
        tell application "Safari" to activate
        delay 2
        tell process "Safari"
            set frontmost to true
            click menu item "Settings…" of menu 1 of menu bar item "Safari" of menu bar 1
            delay 1
            click button "Advanced" of toolbar 1 of window 1
            tell checkbox "Show Develop menu in menu bar" of group 1 of group 1 of window 1
                if value is 0 then click it
            end tell
            click button 1 of window 1
            click menu item "Allow Remote Automation" of menu 1 of menu bar item "Develop" of menu bar 1
        end tell
        log "Finished Safari setup"
    end tell
end

try
    setupSafari()

on error error_message number error_number

    if error_number = -1743 then
        log "Please enable 'Privacy & Security' > 'Automation' > 'Terminal' > 'System Events' before restarting setup.sh"

    else if error_number = -1719 then
        log "Please enable 'Privacy & Security' > 'Accessibility' > 'Terminal' before restarting setup.sh"

    else
        log "Failed Safari setup. " & error_message & " (" & error_number & "). Check the README to see how to set up Safari manually"
    end if
end try
tell application "Safari" to quit saving no
