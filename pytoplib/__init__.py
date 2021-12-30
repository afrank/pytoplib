#!/usr/bin/python3

import json
import curses
from pyrallel import Pyrallel
import threading

class Display(threading.Thread):
    def __init__(self, q, shutdown, display_fields, sort_field=None, sort_reverse=False, key_map={}):
        super().__init__()
        self.q = q
        self.shutdown = shutdown
        self.display = {}
        self.key_map = key_map
        self.sort_field = sort_field
        self.sort_reverse = sort_reverse
        self.stdscr = curses.initscr()
        #self.stdscr = None # setting this to None bypasses curses for debugging
        self.maxwidth = 0

        if self.stdscr:
            _, self.maxwidth = self.stdscr.getmaxyx()

        self.display_fields = display_fields

    def build_lines(self):
        keys = self.display.keys()

        lines = []

        for k in keys:
            obj = self.display[k]

            lines += [obj]

        return lines

    def update(self):
        lines = self.build_lines()
        lstrs = []

        header = ""
        x = {}
        for f in self.display_fields:
            maxlen = f[2]
            if maxlen == -1:
                maxlen = self.maxwidth - sum([ z for x,y,z in self.display_fields if z > -1 ]) - 5
            header += getattr(f[0], f[1])(maxlen)
            x[f[0]] = (f[1], f[2])

        for line in lines:
            lstr = ""
            for f in self.display_fields:
                key = f[0]
                fmt = f[1]
                maxlen = f[2]
                if maxlen == -1:
                    maxlen = self.maxwidth - sum([ z for x,y,z in self.display_fields if z > -1 ]) - 5
                lstr += getattr(str(line[key])[0:maxlen], fmt)(maxlen)
            lstrs += [lstr]

        if self.stdscr:
            self.stdscr.clear()
            self.stdscr.addstr(header + "\n", curses.A_REVERSE)
        else:
            print(header)


        for line in lstrs:
            if self.stdscr:
                self.stdscr.addstr( line + "\n" )
            else:
                print(line)

        if self.stdscr:
            self.stdscr.refresh()

    def run(self):
        while not self.shutdown():
            item = None
            do_update = False
            try:
                item = self.q.get(timeout=1)
            except:
                pass
            if item:
                host, ts, stdout, stderr = item
                d = json.loads(stdout)
                k = host
                if k in self.key_map:
                    k = self.key_map[k]
                self.display[k] = d
                do_update = True

            if do_update:
                self.update()
                do_update = False

        if self.stdscr:
            curses.endwin()

