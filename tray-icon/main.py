#!/usr/bin/env python3
"""Main entry point for tray icon application."""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from indicator import PlannerIndicator


def main():
    """Start the tray icon application."""
    indicator = PlannerIndicator()
    Gtk.main()


if __name__ == '__main__':
    main()
