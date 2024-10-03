# dtimer\_py
DTimer was designed to be used as a timer for work,
Specifically for Data Annotation Tech.

*Created by:* John McCabe-Dansted (and code snippets from StackOverflow)

If you want to work for DAT you can use my referral code:
2ZbHGEA

New in 0.8: Support Wayland? Switch to DataAnnotation Window before copying DAT info.
New in 0.7: Move old GUI to 0,0 if started again
New in 0.6: DAT\_EXTENSIONS (Enter Work Time) and LOG\_TIME
New in 0.5: UI Enhancements, Doom Clock supports <1hr too.
New in 0.4: Removed Linux dependancy on Unifont
New in 0.3: Tested and fixed install on Ubuntu
New in 0.2: Basic Linux Support and offers to download missing files
  - What works in Linux may depend on your window manager

*TODO:* Support MacOS, Reduce size of logs, check that use of CC-BY-SA StackOverflow code is Fair Use or Compatible with LGPL.
*Bug:*  Sometimes the GUI disapears behind the taskbar.
      Set TaskBar to autohide or open log/dtimer\_TIMESTAMP.tsv
      If you run it again, the old process should reappear at 0,0

## Features
- 3 Clocks:
    * Billable Minutes
    * Doom Clock (Countdown to Deadline)
    * Wall Clock (Current Time)
- Pomodoro (Button turns red when work/play time is up)
- Record Time each Windows spends in the Foreground
    * Recorded as IDLE if the user is away for 1+ minutes
Right Click Menu:
- Copy: Foreground Window Times
- Fix Time: Adjust which window titles are billable
- Doom ^A^C: Copy All Text, Initialize Doom Clock from Clipboard
- Doom Picker: Manually set Deadline
--------------------------------------------
- Restart: Set Billable time etc. to Zero
- Quit: Stop This program
--------------------------------------------
- Help: Show Help
