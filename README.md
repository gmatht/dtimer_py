# dtimer\_py
I wasn't happy with the existing time management software, 
so I made [a Python script](https://github.com/gmatht/joshell/blob/816b51707416b444111e07b74489d552e12bcd78/py/dtimer.pyw) to record my time.
It records window titles so you can audit how you spent your time and a deadline clock.
You should be able to tweak it to fit your needs.
I tweaked it for use with Data Annotation Tech; For example, it warns you if you are recording billable time but have not Enter(ed) Work Mode on DAT's website.
If you aren't going to work with DAT, you probably want to set DAT_EXTENSIONS to false.
<p align="center">
 <img src="https://github.com/user-attachments/assets/e41fb731-dfb4-45ac-9ffe-82aa835dfd9f" alt="DTimer Screenshot" width="50%">
</p>

*Created by:* John McCabe-Dansted (and code snippets from StackOverflow)

If you want to work for DAT you can use my referral code:
2ZbHGEA

**Changelog:**
 - 0.91: Drag and Drop Screenshot menu item added
 - 0.9: Better Linux support, autoclick DAT logo to get doomtime
 - 0.8: Support Wayland? Switch to DataAnnotation Window before copying DAT info.
 - 0.7: Move old GUI to 0,0 if started again
 - 0.6: DAT\_EXTENSIONS (Enter Work Time) and LOG\_TIME
 - 0.5: UI Enhancements, Doom Clock supports <1hr too.
 - 0.4: Removed Linux dependancy on Unifont
 - 0.3: Tested and fixed install on Ubuntu
 - 0.2: Basic Linux Support and offers to download missing files
  

*TODO:* Support MacOS, Reduce size of logs, check that use of CC-BY-SA StackOverflow code is Fair Use or Compatible with LGPL.

*Bug:*  Sometimes the GUI disapears behind the taskbar.
      Set TaskBar to autohide or open log/dtimer\_TIMESTAMP.tsv.
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
