#!/bin/bash

# Create sounds directory
mkdir -p sounds

# Copy default sounds from system
echo "Copying default sounds..."

if [ -f "/usr/share/sounds/freedesktop/stereo/complete.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/complete.oga sounds/
    echo "✓ Copied complete.oga"
fi

if [ -f "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/dialog-warning.oga sounds/reminder.oga
    echo "✓ Copied reminder.oga"
fi

if [ -f "/usr/share/sounds/freedesktop/stereo/bell.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/bell.oga sounds/alert.oga
    echo "✓ Copied alert.oga"
fi

echo "Sound setup complete!"
echo "Custom sounds directory: $(pwd)/sounds"
