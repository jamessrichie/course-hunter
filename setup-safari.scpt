on setupSafari()
    try
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
            tell application "Safari" to quit saving no
            log "Finished Safari setup"
        end tell

    on error error_message number error_number
        tell application "Safari" to quit saving no

        if error_number = -1743 or error_number = -1719 then

            if error_number = -1743 then
                log "Please enable 'Privacy & Security' > 'Automation' > 'Terminal' > 'System Events'"
            else if error_number = -1719 then
                log "Please enable 'Privacy & Security' > 'Accessibility' > 'Terminal'"
            end if

            log "Once enabled, close System Settings to continue setup"
            delay 2

            tell application "System Settings" to activate
            repeat while application "System Settings" is running
                delay 0.5
            end repeat

            log "Continuing setup"
            setupSafari()

        else
            log "Failed Safari setup. " & error_message & " (" & error_number & "). Check the README to see how to set up Safari manually"
        end if
    end try
end

log "Setting up Safari..."
setupSafari()