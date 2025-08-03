# Notes Calendar App

A modern, clean desktop calendar application built with Python and CustomTkinter. Features a beautiful rounded design with note-taking capabilities.

## Features

- 📅 **Month List**: Clean list of all months with note counters
- 🗓️ **Calendar View**: Full calendar display for each month
- 📝 **Note Taking**: Add and save notes for any day
- 💾 **JSON Storage**: All notes are saved to `notes.json`
- 🎨 **Modern UI**: Rounded corners and clean design
- 🔄 **Real-time Updates**: Note counters update automatically
- 📱 **Responsive**: Adapts to different window sizes

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://python.org)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   python calendar_app.py
   ```

2. **Using the app**:
   - **Left Panel**: Click on any month to view its calendar
   - **Right Panel**: Click on any day to add/edit notes
   - **Note Counters**: Shows the number of notes for each month
   - **Save Notes**: Click "💾 Save Notes" to save your notes
   - **Clear Notes**: Click "🗑️ Clear Notes" to clear the current notes

## File Structure

```
Calender/
├── calendar_app.py      # Main application
├── requirements.txt     # Python dependencies
├── README.md          # This file
└── notes.json         # Notes storage (created automatically)
```

## Features in Detail

### Month List (Left Panel)
- Shows all 12 months with their numbers (01 January, 02 February, etc.)
- Displays note counters next to each month
- Clean, rounded button design
- Hover effects for better UX

### Calendar View (Right Panel)
- Full month calendar display
- Days with notes are highlighted in blue
- Note indicators (📝) appear on days with notes
- Back button to return to month list

### Notes Panel
- Large text area for writing notes
- Save and Clear buttons
- Success message when notes are saved
- Automatic loading of existing notes

### Data Storage
- All notes are saved to `notes.json`
- Structured by year → month → day → notes
- Automatic backup and recovery
- No data loss on app restart

## Customization

The app uses CustomTkinter's dark theme by default. You can modify the appearance by changing these lines in `calendar_app.py`:

```python
ctk.set_appearance_mode("dark")  # Change to "light" for light theme
ctk.set_default_color_theme("blue")  # Change to "green", "dark-blue", etc.
```

## Troubleshooting

- **App won't start**: Make sure you have Python 3.7+ installed
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Notes not saving**: Check that the app has write permissions in the directory
- **UI looks wrong**: Try updating CustomTkinter: `pip install --upgrade customtkinter`

## License

This project is open source and available under the MIT License. 