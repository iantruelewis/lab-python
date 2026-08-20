# Typing Speed Test
# 1. Establish terminal standard screen wrapper to run test inside terminal
# 2. Establish color relationship of text types (current vs. target)
# 3. Write current text to overlap target text
# 4. Calculate WPM and connect to "time"
# 5. Defense against failure states / errors in logic
# 6. End test / success state
# 7. Allow users to test again
# 8. Randomize test text from text.txt file
###

# accesses Text User Interfaces library directly in command-line terminal
import curses
# helper function that safely intializes and deinitializes terminal environment
from curses import wrapper
# time as seconds since epoch
import time
# allows for randomization
import random

# creates starting screen for user to begin test
def start_screen(stdscr):
    stdscr.clear()
    # welcome message / instructions
    stdscr.addstr("Welcome to the Speed Typing Test!")
    stdscr.addstr("\nPress any key to begin...")
    stdscr.refresh()
    stdscr.getkey()

# creates display text for user, color change / comparison
def display_text(stdscr, target, current, wpm=0):
    stdscr.addstr(target)
    # embeds python expression for WPM without having to concatenate two strings
    stdscr.addstr(1, 0, f"WPM: {wpm}")
            
    # enumerate gives element from current as well as the index in the list
    for i, char in enumerate(current):
        correct_char = target[i]
        color = curses.color_pair(1)
        if char != correct_char:
            color = curses.color_pair(2)

        stdscr.addstr(0, i, char, color)

# randomly chooses test text from text.txt file for user
def load_text():
    with open("text.txt", "r") as f: # context manager to ensure all lines of file are read
        lines = f.readlines()
        return random.choice(lines).strip() # imports random string, removes "\n" from text list element

# words per minute test
def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    wpm = 0
    # time since epoch in seconds
    start_time = time.time()
    # unblocks getkey()
    stdscr.nodelay(True)

    #while loop processing current_text overlapping target_text
    while True:
        # subtracts start_time from time since epoch in seconds
        # adding "1" circumvents the possibility of a divide by zero error
        time_elapsed = max(time.time() - start_time, 1)
        # equation for calculating wpm: characters per minute divided by 5 = words per minute
        wpm = round((len(current_text) / (time_elapsed / 60)) / 5) # round to avoid decimals

        # overlapping text over test case
        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm)
        stdscr.refresh()

        # checks for success state / ends test
        if "".join(current_text) == target_text:  # converts list to string(s)
            stdscr.nodelay(False)
            break

        # ensures program won't crash if user doesn't type input
        try:
            key = stdscr.getkey()
        except:
            continue

        # ordinal value of "Escape" key in ASCII = 27
        if ord(key) == 27:
            break

        # backspace failure management
        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()
        # circumvents out of bounds exception / indexing issue
        elif len(current_text) < len(target_text):
            current_text.append(key)

# calls a standard screen for main function to initiate testing area within terminal
def main(stdscr):
    # creates colored text in testing environment
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    # while loop to allow users to play another round
    while True:
        wpm_test(stdscr)
        stdscr.addstr(2, 0, "You completed the text! Press any key to continue...")
        # ordinal value of escape key allows user to "leave" test
        key = stdscr.getkey()
        if ord(key) == 27:
            break

# wrapper calls main within terminal environment
wrapper(main)