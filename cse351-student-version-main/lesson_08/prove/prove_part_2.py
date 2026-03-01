"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Dylan

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

<Answer here>

Why would it work?

<Answer here>

"""

import math
import os
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global stop, thread_count

    stop = False
    thread_count = 1          # count the initial (main) thread

    # this list is only used for reference; joining happens locally in _walk
    # the lock is not strictly needed for append under GIL but kept for clarity
    thread_list = []

    def _walk(row, col, color):
        """Recursive worker; forks spawn threads."""
        nonlocal thread_list
        global stop, thread_count

        if stop or not maze.can_move_here(row, col):
            return

        maze.move(row, col, color)
        if maze.at_end(row, col):
            stop = True
            return

        moves = maze.get_possible_moves(row, col)
        local_threads = []
        first = True
        for (nr, nc) in moves:
            if stop: break
            if first:
                first = False
                _walk(nr, nc, color)
            else:
                new_color = get_color()
                thread_count += 1
                t = threading.Thread(target=_walk, args=(nr, nc, new_color))
                local_threads.append(t)
                thread_list.append(t)
                t.start()

        for t in local_threads:
            t.join()

    # kick off the recursion from the start position with a fresh color
    start_color = get_color()
    start = maze.get_start_pos()
    _walk(start[0], start[1], start_color)

    # all threads should have been joined via the recursion, but join any remaining
    for t in thread_list:
        t.join()




def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    script_dir = os.path.dirname(__file__)
    mazes_dir = os.path.join(script_dir, 'mazes')

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filepath = os.path.join(mazes_dir, filename)
        log.write()
        log.write(f'File: {filepath}')
        find_end(log, filepath, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()