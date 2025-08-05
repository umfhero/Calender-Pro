import customtkinter as ctk
import calendar
import json
import os
import sys
import tkinter as tk
from datetime import datetime
from typing import Dict, List, Any
from PIL import Image, ImageTk
from tkinter import filedialog

# Configure the appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_storage_settings():
    """Load storage location settings from config file."""
    # Default location to OneDrive folder
    default_location = r"C:\Users\umfhe\OneDrive - Middlesex University\A - Calendar Pro"

    # Create the default directory if it doesn't exist
    if not os.path.exists(default_location):
        try:
            os.makedirs(default_location, exist_ok=True)
        except:
            # If we can't create the OneDrive folder, fall back to current directory
            default_location = os.getcwd()

    settings_file = 'calendar_settings.json'
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get('storage_location', default_location)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_location
    return default_location


def save_storage_settings(storage_location):
    """Save storage location settings to config file."""
    settings = {'storage_location': storage_location}
    with open('calendar_settings.json', 'w') as f:
        json.dump(settings, f, indent=4)


def get_data_file_path(filename):
    """Get the full path for a data file based on storage location setting."""
    storage_location = load_storage_settings()
    return os.path.join(storage_location, filename)


class CalendarApp(ctk.CTk):
    """
    A modern desktop calendar application for viewing months, adding notes,
    and tracking notes per month with a clean, rounded design.
    """

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Calendar Pro")
        self.geometry("1000x800")
        self.minsize(800, 700)

        # Set app icon with multiple methods for better compatibility
        self.set_window_icon()

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize storage location
        self.storage_location = load_storage_settings()

        # Load existing notes
        self.note_data = self.load_notes()
        self.timetable_data = self.load_timetable()  # Load timetable data
        self.modules_data = self.load_modules()  # Load modules data

        # Add preset module if no modules exist
        if not self.modules_data:
            self.modules_data = {
                "CST3510 Memory Analysis": {
                    "color": "#45B7D1",
                    "teacher": "Mr David Neilson",
                    "rooms": ["Room Unknown", "Lab A", "Lab B", "Lecture Hall 1", "Lecture Hall 2"],
                    "created": datetime.now().isoformat()
                }
            }
            self.save_modules()

        self.current_month = None
        self.delete_mode = False
        self.selected_days = set()  # Track selected days for deletion

        # Create the main layout
        self.create_left_panel()
        self.create_right_panel()

        # Initialize with welcome message and highlight current month
        self.show_months_list()

        # Force icon setting after window is fully initialized
        self.after(100, self.set_window_icon)

    def set_window_icon(self):
        """Sets the window icon using multiple fallback methods."""
        icon_set = False

        # Method 1: Try iconbitmap with .ico file
        try:
            self.iconbitmap(resource_path("calendar.ico"))
            icon_set = True
        except:
            pass

        # Method 1b: Try wm_iconbitmap as alternative
        try:
            self.wm_iconbitmap(resource_path("calendar.ico"))
            icon_set = True
        except:
            pass

        # Method 2: Try iconphoto with PNG converted to PhotoImage
        try:
            icon_img = tk.PhotoImage(file=resource_path("icon.png"))
            self.iconphoto(True, icon_img)
            icon_set = True
        except:
            pass

        # Method 3: Try using PIL to load and convert the icon
        try:
            from PIL import Image, ImageTk
            # Load icon.png and convert to PhotoImage
            pil_img = Image.open(resource_path("icon.png"))
            # Resize to standard icon size if needed
            pil_img = pil_img.resize((32, 32), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.iconphoto(True, tk_img)
            # Keep reference to prevent garbage collection
            self._icon_image = tk_img
            icon_set = True
        except:
            pass

        # Method 4: Try with .ico file converted through PIL
        try:
            from PIL import Image, ImageTk
            pil_img = Image.open(resource_path("calendar.ico"))
            pil_img = pil_img.resize((32, 32), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.iconphoto(True, tk_img)
            self._icon_image = tk_img
            icon_set = True
        except:
            pass

    def create_left_panel(self):
        """Creates the left panel with month list and note counters."""
        # Left Frame for Months
        self.left_frame = ctk.CTkFrame(self, width=250, corner_radius=15)
        self.left_frame.grid(
            row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.left_frame.grid_propagate(False)
        self.left_frame.configure(width=250)

        # Configure left frame grid
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=0)  # For notifications
        # Adjust for timetable and settings buttons (row 13 + 2)
        self.left_frame.grid_rowconfigure(15, weight=1)

        # Home button at the top
        home_btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        home_btn_frame.grid(row=0, column=0, padx=15,
                            pady=(10, 5), sticky="ew")

        # Load home icon
        home_icon = None
        try:
            home_icon = ctk.CTkImage(
                light_image=Image.open(resource_path("house.ico")),
                dark_image=Image.open(resource_path("house.ico")),
                size=(37, 37)
            )
        except:
            pass

        home_btn = ctk.CTkButton(
            home_btn_frame,
            text="  Home" if not home_icon else "",
            image=home_icon,
            compound="left",
            command=self.show_months_list,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47"),
            text_color=("white", "white"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            width=220
        )
        home_btn.pack(fill="x")

        # Time Table button
        timetable_btn_frame = ctk.CTkFrame(
            self.left_frame, fg_color="transparent")
        timetable_btn_frame.grid(
            row=1, column=0, padx=15, pady=(5, 5), sticky="ew")

        # Load time table icon (using edit icon as placeholder)
        timetable_icon = None
        try:
            timetable_icon = ctk.CTkImage(
                light_image=Image.open(resource_path("edit.png")),
                dark_image=Image.open(resource_path("edit.png")),
                size=(37, 37)
            )
        except:
            pass

        timetable_btn = ctk.CTkButton(
            timetable_btn_frame,
            text="  Time Table",
            image=timetable_icon,
            compound="left",
            command=self.show_timetable,
            fg_color=("#482728", "#482728"),
            hover_color=("#5A3233", "#5A3233"),
            text_color=("white", "white"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            width=220
        )
        timetable_btn.pack(fill="x")

        # Settings button
        settings_btn_frame = ctk.CTkFrame(
            self.left_frame, fg_color="transparent")
        settings_btn_frame.grid(
            row=2, column=0, padx=15, pady=(5, 5), sticky="ew")

        # Load settings icon (using edit icon as placeholder)
        settings_icon = None
        try:
            settings_icon = ctk.CTkImage(
                light_image=Image.open(resource_path("edit.png")),
                dark_image=Image.open(resource_path("edit.png")),
                size=(37, 37)
            )
        except:
            pass

        settings_btn = ctk.CTkButton(
            settings_btn_frame,
            text="  Settings",
            image=settings_icon,
            compound="left",
            command=self.show_settings,
            fg_color=("#2E4057", "#2E4057"),
            hover_color=("#3A506B", "#3A506B"),
            text_color=("white", "white"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            width=220
        )
        settings_btn.pack(fill="x")

        # Month buttons container
        self.month_buttons = {}
        self.month_note_labels = {}
        self.create_month_list()

    def create_month_list(self):
        """Populates the left frame with buttons for each month of the year."""
        current_year = datetime.now().year
        current_month = datetime.now().month

        for i in range(1, 13):
            month_name = calendar.month_name[i]
            month_data = self.note_data.get(
                str(current_year), {}).get(month_name, {})
            note_count = len(
                [day for day, notes in month_data.items() if notes])
            is_current_month = (i == current_month)

            # Create button container with rounded corners (adjust row to i+2 for timetable and settings buttons)
            btn_container = ctk.CTkFrame(
                self.left_frame, corner_radius=12, fg_color="transparent")
            btn_container.grid(row=i+2, column=0, padx=15, pady=2, sticky="ew")

            # Month button with current month highlighting
            notification_text = f"{i} {month_name}"
            notification_fg_color = (
                "#0B2027", "#0B2027") if is_current_month else ("gray90", "gray10")
            notification_hover_color = (
                "#1A3A47", "#1A3A47") if is_current_month else ("gray85", "gray15")

            month_btn = ctk.CTkButton(
                btn_container,
                text=notification_text,
                command=lambda month_num=i: self.show_calendar(month_num),
                anchor="w",
                fg_color=notification_fg_color,
                hover_color=notification_hover_color,
                text_color=("white", "white") if is_current_month else (
                    "gray20", "gray80"),
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=10,
                height=40,
                width=220
            )
            month_btn.pack(side="left", padx=5, pady=5, fill="x", expand=True)

            # Add notification icon outside the button container if there are notes
            if note_count > 0:
                # Create notification frame outside the button container
                notification_frame = ctk.CTkFrame(
                    self.left_frame, fg_color="transparent")
                notification_frame.grid(
                    row=i+2, column=1, padx=(5, 15), pady=2, sticky="ne")

                # Try using Canvas to overlay text on image without background
                import tkinter as tk
                canvas = tk.Canvas(
                    notification_frame,
                    width=42,
                    height=42,
                    highlightthickness=0,
                    bg='#dbdbdb'  # Use the exact background color you mentioned
                )
                canvas.pack()

                # Load and draw the icon image on canvas
                try:
                    from PIL import ImageTk
                    icon_pil = Image.open(resource_path(
                        "bell.png")).resize((42, 42))
                    icon_photo = ImageTk.PhotoImage(icon_pil)
                    canvas.create_image(21, 21, image=icon_photo)
                    # Keep a reference to prevent garbage collection
                    canvas.image = icon_photo

                    # Draw text with black color (no background circle)
                    canvas.create_text(21, 21, text=str(note_count),
                                       font=("Arial", 14, "bold"),
                                       fill="black")
                except Exception as e:
                    # Fallback to simple colored circle with text
                    canvas.create_oval(
                        5, 5, 37, 37, fill="red", outline="white", width=2)
                    canvas.create_text(21, 21, text=str(note_count),
                                       font=("Arial", 16, "bold"),
                                       fill="white")

            self.month_buttons[month_name] = month_btn
            # Store notification counter for updates
            if note_count > 0:
                # Store canvas instead
                self.month_note_labels[month_name] = canvas
            else:
                self.month_note_labels[month_name] = None

    def create_right_panel(self):
        """Creates the right panel for calendar display."""
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(
            row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

    def clear_right_frame(self):
        """Destroys all widgets in the right frame to prepare for new content."""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_calendar(self, month_num):
        """Displays a calendar for a selected month and allows adding notes."""
        self.clear_right_frame()
        self.current_month = month_num
        current_year = datetime.now().year
        month_name = calendar.month_name[month_num]

        # Configure right frame grid
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # Header with back button and delete controls
        header_frame = ctk.CTkFrame(
            self.right_frame, fg_color="transparent", corner_radius=10)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(2, weight=1)

        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Months",
            command=self.show_months_list,
            fg_color="transparent",
            text_color=("#0B2027", "#0B2027"),
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=30
        )
        back_btn.grid(row=0, column=0, padx=(0, 10))

        # Delete mode controls
        if not self.delete_mode:
            delete_btn = ctk.CTkButton(
                header_frame,
                text="🗑️ Delete Notes",
                command=self.enter_delete_mode,
                fg_color=("red", "darkred"),
                hover_color=("darkred", "red"),
                font=ctk.CTkFont(size=12),
                corner_radius=8,
                height=30
            )
            delete_btn.grid(row=0, column=1, padx=(0, 10))
        else:
            # Delete mode controls frame
            delete_controls = ctk.CTkFrame(
                header_frame, fg_color="transparent")
            delete_controls.grid(row=0, column=1, padx=(0, 10))

            confirm_btn = ctk.CTkButton(
                delete_controls,
                text=f"✓ Delete {len(self.selected_days)} Days",
                command=self.confirm_delete_selected,
                fg_color=("red", "darkred"),
                hover_color=("darkred", "red"),
                font=ctk.CTkFont(size=11),
                corner_radius=8,
                height=30,
                width=120
            )
            confirm_btn.pack(side="left", padx=(0, 5))

            cancel_btn = ctk.CTkButton(
                delete_controls,
                text="✕ Cancel",
                command=self.exit_delete_mode,
                fg_color=("gray", "darkgray"),
                hover_color=("darkgray", "gray"),
                font=ctk.CTkFont(size=11),
                corner_radius=8,
                height=30,
                width=60
            )
            cancel_btn.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{month_name} ({current_year})" +
            (" - Select days to delete" if self.delete_mode else ""),
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=2, sticky="w")

        # Calendar container
        calendar_frame = ctk.CTkFrame(self.right_frame, corner_radius=15)
        calendar_frame.grid(row=1, column=0, padx=20,
                            pady=(0, 20), sticky="nsew")
        calendar_frame.grid_columnconfigure(0, weight=1)
        calendar_frame.grid_rowconfigure(1, weight=1)

        # Weekdays header
        weekdays_frame = ctk.CTkFrame(calendar_frame, fg_color="transparent")
        weekdays_frame.grid(row=0, column=0, padx=20,
                            pady=(20, 10), sticky="ew")

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(weekdays):
            weekday_label = ctk.CTkLabel(
                weekdays_frame,
                text=day,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("gray30", "gray70")
            )
            weekday_label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            weekdays_frame.grid_columnconfigure(col, weight=1)

        # Days grid
        days_frame = ctk.CTkFrame(calendar_frame, fg_color="transparent")
        days_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Configure days frame grid
        for i in range(7):
            days_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            days_frame.grid_rowconfigure(i, weight=1)

        cal = calendar.Calendar()

        # Populate calendar days
        row, col = 0, 0
        current_day = datetime.now().day
        current_month = datetime.now().month
        is_current_month_view = (month_num == current_month)

        for day in cal.itermonthdays(current_year, month_num):
            if day == 0:
                # Empty cell for days outside the month
                empty_label = ctk.CTkLabel(
                    days_frame, text="", fg_color="transparent")
                empty_label.grid(row=row, column=col, padx=2,
                                 pady=2, sticky="nsew")
                col = (col + 1) % 7
                if col == 0:
                    row += 1
                continue

            # Check if there are notes for this day
            day_notes = self.note_data.get(str(current_year), {}).get(
                month_name, {}).get(str(day), [])
            has_notes = len(day_notes) > 0

            # Check if this is the current day (only highlight if viewing current month)
            is_current_day = (is_current_month_view and day == current_day)

            # Check if this day is selected for deletion
            is_selected = day in self.selected_days

            # Determine button colors based on notes, current day, and selection
            if self.delete_mode and is_selected:
                # Selected for deletion
                fg_color = ("orange", "darkorange")
                hover_color = ("darkorange", "orange")
                text_color = ("white", "white")
            elif is_current_day:
                # Current day gets the new color highlight
                fg_color = ("#0B2027", "#0B2027")
                hover_color = ("#1A3A47", "#1A3A47")
                text_color = ("white", "white")
            elif has_notes:
                # Days with notes get the new color highlight
                fg_color = ("#6DB176", "#6DB176")
                hover_color = ("#83CC8D", "#83CC8D")
                text_color = ("white", "white")
            else:
                # Regular days
                fg_color = ("gray95", "gray5")
                hover_color = ("gray90", "gray10")
                text_color = ("gray20", "gray80")

            # Create day button with appropriate command
            if self.delete_mode:
                def command(d=day): return self.toggle_day_selection(
                    d, current_year, month_name)
            else:
                def command(d=day): return self.show_notes_panel(
                    current_year, month_name, d)

            # Create day button
            day_btn = ctk.CTkButton(
                days_frame,
                text=str(day),
                command=command,
                width=60,
                height=60,
                corner_radius=12,
                fg_color=fg_color,
                hover_color=hover_color,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=text_color
            )
            day_btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            # Add note indicator if there are notes (but not if it's the current day or selected)
            if has_notes and not is_current_day and not (self.delete_mode and is_selected):
                note_indicator = ctk.CTkLabel(
                    days_frame,
                    text=f"📝",
                    font=ctk.CTkFont(size=10),
                    fg_color="transparent"
                )
                note_indicator.grid(row=row, column=col, padx=(
                    40, 0), pady=(0, 20), sticky="ne")

            # Add selection indicator if in delete mode and selected
            if self.delete_mode and is_selected:
                selection_indicator = ctk.CTkLabel(
                    days_frame,
                    text="✓",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("white", "white"),
                    fg_color="transparent"
                )
                selection_indicator.grid(row=row, column=col, padx=(
                    40, 0), pady=(5, 0), sticky="ne")

            col = (col + 1) % 7
            if col == 0:
                row += 1

    def show_months_list(self):
        """Shows the months list on the left panel."""
        self.clear_right_frame()
        self.current_month = None
        self.delete_mode = False
        self.selected_days = set()

        # Welcome message
        welcome_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Get current date and time
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        current_time = now.strftime("%I:%M %p")

        # Welcome header with home icon
        welcome_header_frame = ctk.CTkFrame(
            welcome_frame, fg_color="transparent")
        welcome_header_frame.pack(pady=(30, 10))

        # Load home icon for welcome screen
        home_icon_welcome = None
        try:
            home_icon_welcome = ctk.CTkImage(
                light_image=Image.open(resource_path("house.ico")),
                dark_image=Image.open(resource_path("house.ico")),
                size=(48, 48)
            )
        except:
            pass

        if home_icon_welcome:
            home_icon_label = ctk.CTkLabel(
                welcome_header_frame,
                text="",
                image=home_icon_welcome,
                fg_color="transparent"
            )
            home_icon_label.pack(side="left", padx=(0, 10))

        welcome_label = ctk.CTkLabel(
            welcome_header_frame,
            text="Welcome to Calendar Pro!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        welcome_label.pack(side="left")

        # Current date and time display - much bigger
        date_time_label = ctk.CTkLabel(
            welcome_frame,
            text=f"{current_date}\n🕐 {current_time}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("black", "black")
        )
        date_time_label.pack(pady=(40, 20))

        instruction_label = ctk.CTkLabel(
            welcome_frame,
            text="Select a month from the left panel to view the calendar and add notes.",
            font=ctk.CTkFont(size=16),
            text_color=("gray40", "gray60")
        )
        instruction_label.pack(pady=(0, 20))

        # Recent notes panel with background container
        recent_notes_container = ctk.CTkFrame(
            welcome_frame, corner_radius=15, fg_color=("gray95", "gray10"))
        recent_notes_container.pack(fill="x", padx=20, pady=10)

        recent_notes_frame = ctk.CTkFrame(
            recent_notes_container, fg_color="transparent")
        recent_notes_frame.pack(fill="x", padx=15, pady=15)

        recent_title = ctk.CTkLabel(
            recent_notes_frame,
            text="Recent Notes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        recent_title.pack(pady=(0, 15))

        # Get recent notes with countdown
        recent_notes = self.get_recent_notes()
        if recent_notes:
            for note_info in recent_notes:
                # Create a frame for each note
                note_frame = ctk.CTkFrame(
                    recent_notes_frame, fg_color="transparent")
                note_frame.pack(fill="x", padx=20, pady=5, anchor="w")

                # Date and countdown header
                header_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
                header_frame.pack(fill="x", pady=(0, 8))

                date_label = ctk.CTkLabel(
                    header_frame,
                    text=f"• {note_info['date']} - {note_info['countdown']}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#0B2027", "#0B2027"),
                    anchor="w"
                )
                date_label.pack(side="left", anchor="w")

                # Button frame for edit button
                btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                btn_frame.pack(side="right", padx=(10, 0))

                # Edit button (opens editable window)
                # Load edit icon
                edit_icon = None
                try:
                    edit_icon = ctk.CTkImage(
                        light_image=Image.open(resource_path("edit.png")),
                        dark_image=Image.open(resource_path("edit.png")),
                        size=(36, 36)
                    )
                except:
                    pass

                edit_btn = ctk.CTkButton(
                    btn_frame,
                    text="Edit" if not edit_icon else "",
                    image=edit_icon,
                    compound="left",
                    command=lambda n=note_info: self.edit_note_in_window(n),
                    fg_color="transparent",
                    text_color=("#0B2027", "#0B2027"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    corner_radius=8,
                    height=25,
                    width=70
                )
                edit_btn.pack(side="left")

                # Note content display
                if note_info['notes']:
                    # Show first line with preview
                    first_line = note_info['notes'][0]
                    preview_text = first_line[:50] + \
                        "..." if len(first_line) > 50 else first_line

                    note_preview = ctk.CTkLabel(
                        note_frame,
                        text=f"{preview_text}",
                        font=ctk.CTkFont(size=15),
                        text_color=("gray20", "gray80"),
                        anchor="w",
                        justify="left"
                    )
                    note_preview.pack(padx=20, pady=(0, 8), anchor="w")
                else:
                    no_content_label = ctk.CTkLabel(
                        note_frame,
                        text="> No note content",
                        font=ctk.CTkFont(size=15),
                        text_color=("gray50", "gray70"),
                        anchor="w"
                    )
                    no_content_label.pack(padx=20, pady=(0, 8), anchor="w")
        else:
            no_notes_label = ctk.CTkLabel(
                recent_notes_frame,
                text="No recent notes found",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray60")
            )
            no_notes_label.pack(pady=10)

        recent_notes_frame.pack_configure(pady=(0, 20))

    def show_notes_panel(self, year, month_name, day):
        """Displays a notes panel for a specific day."""
        self.clear_right_frame()

        # Configure right frame grid
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Calendar",
            command=lambda: self.show_calendar(self.current_month),
            fg_color="transparent",
            text_color=("#0B2027", "#0B2027"),
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=30
        )
        back_btn.grid(row=0, column=0, padx=(0, 10))

        notes_title = ctk.CTkLabel(
            header_frame,
            text=f"Notes for {month_name} {day}, {year}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        notes_title.grid(row=0, column=1, sticky="w")

        # Notes container
        notes_container = ctk.CTkFrame(self.right_frame, corner_radius=15)
        notes_container.grid(row=1, column=0, padx=20,
                             pady=(0, 20), sticky="nsew")
        notes_container.grid_columnconfigure(0, weight=1)
        notes_container.grid_rowconfigure(0, weight=1)

        # Text widget for notes
        self.notes_text = ctk.CTkTextbox(
            notes_container,
            wrap="word",
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.notes_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Load existing notes
        notes = self.note_data.get(str(year), {}).get(
            month_name, {}).get(str(day), [])
        if notes:
            self.notes_text.insert("1.0", "\n".join(notes))

        # Button frame
        btn_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save Notes",
            command=lambda: self.save_notes(
                year, month_name, day, self.notes_text.get("1.0", "end-1c")),
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47")
        )
        save_btn.pack(side="left", padx=10)

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear Notes",
            command=lambda: self.notes_text.delete("1.0", "end"),
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        clear_btn.pack(side="left", padx=10)

    def save_notes(self, year, month_name, day, notes_text):
        """Saves the notes for a specific day to a JSON file."""
        # Split the text by newlines to store as a list of strings
        notes_list = [note.strip()
                      for note in notes_text.split('\n') if note.strip()]

        year_str = str(year)
        day_str = str(day)

        # Ensure the nested dictionary structure exists
        if year_str not in self.note_data:
            self.note_data[year_str] = {}
        if month_name not in self.note_data[year_str]:
            self.note_data[year_str][month_name] = {}

        self.note_data[year_str][month_name][day_str] = notes_list

        # Save to file
        notes_file_path = get_data_file_path('notes.json')
        with open(notes_file_path, 'w') as f:
            json.dump(self.note_data, f, indent=4)

        # Update the month counter on the left panel
        note_count = len(
            [day for day, notes in self.note_data[year_str][month_name].items() if notes])
        self.update_month_notification(month_name, note_count)

        # Show success message
        self.show_success_message()

    def show_success_message(self):
        """Shows a temporary success message."""
        success_label = ctk.CTkLabel(
            self.right_frame,
            text="✅ Notes saved successfully!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        success_label.place(relx=0.5, rely=0.9, anchor="center")

        # Remove the message after 2 seconds
        self.after(2000, success_label.destroy)

    def load_notes(self):
        """Loads notes from the notes.json file."""
        notes_file_path = get_data_file_path('notes.json')
        if os.path.exists(notes_file_path):
            try:
                with open(notes_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def get_recent_notes(self):
        """Gets the 5 most recent notes with countdown to current date."""
        current_date = datetime.now()
        all_notes = []

        # Collect all notes with their dates
        for year_str, year_data in self.note_data.items():
            for month_name, month_data in year_data.items():
                for day_str, notes in month_data.items():
                    if notes:  # Only include days with actual notes
                        try:
                            # Create date object for this note
                            month_num = list(
                                calendar.month_name).index(month_name)
                            note_date = datetime(
                                int(year_str), month_num, int(day_str))

                            # Calculate days difference from current date
                            days_diff = (note_date - current_date).days

                            # Create countdown text
                            if days_diff == 0:
                                countdown = "Today"
                            elif days_diff == 1:
                                countdown = "1 day left"
                            elif days_diff == -1:
                                countdown = "1 day ago"
                            elif days_diff > 1:
                                if days_diff < 7:
                                    countdown = f"{days_diff} days left"
                                else:
                                    weeks = days_diff // 7
                                    remaining_days = days_diff % 7
                                    if remaining_days == 0:
                                        countdown = f"{weeks} week{'s' if weeks > 1 else ''} left"
                                    else:
                                        countdown = f"{weeks} week{'s' if weeks > 1 else ''}, {remaining_days} day{'s' if remaining_days > 1 else ''} left"
                            else:
                                countdown = f"{abs(days_diff)} day{'s' if abs(days_diff) > 1 else ''} ago"

                            all_notes.append({
                                'date': f"{month_name} {day_str}, {year_str}",
                                'countdown': countdown,
                                'days_diff': days_diff,
                                'note_date': note_date,
                                'notes': notes,
                                'year': year_str,
                                'month': month_name,
                                'day': day_str
                            })
                        except (ValueError, TypeError):
                            continue

        # Sort by proximity to current date (closest first)
        all_notes.sort(key=lambda x: abs(x['days_diff']))

        # Return top 5 most recent
        return all_notes[:5]

    def edit_note_from_home(self, note_info):
        """Opens the notes panel for editing a note from the home screen."""
        year = int(note_info['year'])
        month_name = note_info['month']
        day = int(note_info['day'])

        # Find the month number for the month name
        month_num = list(calendar.month_name).index(month_name)

        # Set current month and show the notes panel
        self.current_month = month_num
        self.show_notes_panel(year, month_name, day)

    def edit_note_in_window(self, note_info):
        """Opens an editable window for editing a note from the home screen."""
        # Create a new window for editing the note
        note_window = ctk.CTkToplevel(self)
        note_window.title(f"Edit Note - {note_info['date']}")
        note_window.geometry("500x400")
        note_window.resizable(True, True)

        # Make window always on top
        note_window.attributes("-topmost", True)
        note_window.transient(self)
        note_window.grab_set()

        # Configure grid
        note_window.grid_columnconfigure(0, weight=1)
        note_window.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            note_window,
            text=f"📝 Edit Note for {note_info['date']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Note content in scrollable text widget
        note_text = ctk.CTkTextbox(
            note_window,
            wrap="word",
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        note_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Load the note content
        if note_info['notes']:
            note_text.insert("1.0", "\n".join(note_info['notes']))

        # Button frame
        btn_frame = ctk.CTkFrame(note_window, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(0, 20))

        # Save button
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=lambda: self.save_note_from_window(
                note_info, note_text.get("1.0", "end-1c"), note_window),
            corner_radius=10,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47")
        )
        save_btn.pack(side="left", padx=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=note_window.destroy,
            corner_radius=10,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray", "darkgray"),
            hover_color=("darkgray", "gray")
        )
        cancel_btn.pack(side="left", padx=10)

    def save_note_from_window(self, note_info, notes_text, window):
        """Saves the note from the edit window and updates the UI."""
        # Split the text by newlines to store as a list of strings
        notes_list = [note.strip()
                      for note in notes_text.split('\n') if note.strip()]

        year = int(note_info['year'])
        month_name = note_info['month']
        day = int(note_info['day'])
        year_str = str(year)
        day_str = str(day)

        # Ensure the nested dictionary structure exists
        if year_str not in self.note_data:
            self.note_data[year_str] = {}
        if month_name not in self.note_data[year_str]:
            self.note_data[year_str][month_name] = {}

        self.note_data[year_str][month_name][day_str] = notes_list

        # Save to file
        notes_file_path = get_data_file_path('notes.json')
        with open(notes_file_path, 'w') as f:
            json.dump(self.note_data, f, indent=4)

        # Update the month counter on the left panel
        note_count = len(
            [day for day, notes in self.note_data[year_str][month_name].items() if notes])
        self.update_month_notification(month_name, note_count)

        # Close the window
        window.destroy()

        # Show success message
        self.show_success_message()

    def load_timetable(self):
        """Loads timetable data from the timetable.json file."""
        timetable_file_path = get_data_file_path('timetable.json')
        if os.path.exists(timetable_file_path):
            try:
                with open(timetable_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def save_timetable(self):
        """Saves timetable data to timetable.json file."""
        timetable_file_path = get_data_file_path('timetable.json')
        with open(timetable_file_path, 'w') as f:
            json.dump(self.timetable_data, f, indent=4)

    def load_modules(self):
        """Loads modules data from the modules.json file."""
        modules_file_path = get_data_file_path('modules.json')
        if os.path.exists(modules_file_path):
            try:
                with open(modules_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def save_modules(self):
        """Saves modules data to modules.json file."""
        modules_file_path = get_data_file_path('modules.json')
        with open(modules_file_path, 'w') as f:
            json.dump(self.modules_data, f, indent=4)

    def show_timetable(self):
        """Shows the weekly timetable view."""
        self.clear_right_frame()

        # Configure right frame grid
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Home",
            command=self.show_months_list,
            fg_color="transparent",
            text_color=("#0B2027", "#0B2027"),
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=30
        )
        back_btn.grid(row=0, column=0, padx=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📅 Weekly Time Table",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w")

        # Manage Modules button
        modules_btn = ctk.CTkButton(
            header_frame,
            text="📚 Manage Modules",
            command=self.show_modules_manager,
            fg_color=("#482728", "#482728"),
            hover_color=("#5A3233", "#5A3233"),
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=30
        )
        modules_btn.grid(row=0, column=2, padx=(10, 0))

        # Main timetable container
        timetable_container = ctk.CTkFrame(self.right_frame, corner_radius=15)
        timetable_container.grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        timetable_container.grid_columnconfigure(0, weight=1)
        timetable_container.grid_rowconfigure(0, weight=1)

        # Create scrollable frame for timetable with vertical scrolling
        timetable_scroll = ctk.CTkScrollableFrame(
            timetable_container, corner_radius=10)
        timetable_scroll.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid weights for responsive scaling while maintaining minimum widths
        for i in range(8):  # 7 days + 1 time column
            timetable_scroll.grid_columnconfigure(
                i, weight=1, minsize=120)  # Make all columns same minimum width

        # Configure row weights for responsive height scaling
        for i in range(17):  # Header + 16 time slots (6 AM to 10 PM)
            timetable_scroll.grid_rowconfigure(i, weight=1, minsize=35)

        # Time slots (from 6 AM to 10 PM in 12-hour format - hourly intervals)
        time_slots = []
        for hour in range(6, 22):  # 6 AM to 10 PM
            if hour == 12:
                time_slots.append("12:00 PM")
            elif hour < 12:
                time_slots.append(f"{hour}:00 AM")
            else:
                display_hour = hour - 12
                time_slots.append(f"{display_hour}:00 PM")

        days = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]

        # Create grid header
        # Empty top-left cell with minimum width for time column
        ctk.CTkLabel(
            timetable_scroll,
            text="",
            height=35
        ).grid(row=0, column=0, padx=1, pady=1, sticky="ew")

        # Day headers with responsive width
        for col, day in enumerate(days, 1):
            day_label = ctk.CTkLabel(
                timetable_scroll,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#0B2027", "#0B2027"),
                text_color=("white", "white"),
                corner_radius=6,
                height=35
            )
            day_label.grid(row=0, column=col, padx=1, pady=1, sticky="ew")

        # Time slot rows
        for row, time_slot in enumerate(time_slots, 1):
            # Time label with bigger font and responsive width
            time_label = ctk.CTkLabel(
                timetable_scroll,
                text=time_slot,
                # Increased from 9 to 12
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("gray85", "gray15"),
                corner_radius=4,
                height=35  # Increased height to match other cells
            )
            time_label.grid(row=row, column=0, padx=1, pady=1, sticky="ew")

            # Day cells with responsive width and smaller font
            for col, day in enumerate(days, 1):
                cell_key = f"{day}_{time_slot}"
                cell_data = self.timetable_data.get(cell_key, {})

                cell_text = ""
                cell_color = ("gray95", "gray10")
                text_color = ("gray40", "gray60")

                if cell_data:
                    if cell_data.get('type') == 'lesson':
                        module_name = cell_data.get('module', '')
                        room = cell_data.get('room', '')
                        cell_text = f"{module_name}\n{room}" if room else module_name

                        # Use module color if available
                        if module_name and module_name in self.modules_data:
                            module_color = self.modules_data[module_name].get(
                                'color', '#6DB176')
                            cell_color = (module_color, module_color)
                        else:
                            cell_color = ("#6DB176", "#6DB176")
                        text_color = ("white", "white")
                    elif cell_data.get('type') == 'task':
                        cell_text = f"📋 {cell_data.get('task', '')}"
                        cell_color = ("#4A90E2", "#4A90E2")
                        text_color = ("white", "white")
                    elif cell_data.get('type') == 'blocked':
                        cell_text = "🚫 Blocked"
                        cell_color = ("#FF6B6B", "#FF6B6B")
                        text_color = ("white", "white")

                cell_btn = ctk.CTkButton(
                    timetable_scroll,
                    text=cell_text,
                    command=lambda d=day, t=time_slot: self.edit_timetable_cell(
                        d, t),
                    fg_color=cell_color,
                    hover_color=cell_color,
                    text_color=text_color,
                    font=ctk.CTkFont(size=8),
                    corner_radius=4,
                    height=35  # Increased to match time labels
                )
                cell_btn.grid(row=row, column=col, padx=1, pady=1, sticky="ew")

        # Legend
        legend_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        legend_frame.grid(row=2, column=0, padx=20, pady=(0, 10))

        legend_title = ctk.CTkLabel(
            legend_frame,
            text="Legend:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        legend_title.pack(side="left", padx=(0, 10))

        # Lesson legend
        lesson_legend = ctk.CTkLabel(
            legend_frame,
            text="📚 Lessons",
            fg_color=("#6DB176", "#6DB176"),
            text_color=("white", "white"),
            corner_radius=4,
            width=70,
            height=22,
            font=ctk.CTkFont(size=10)
        )
        lesson_legend.pack(side="left", padx=3)

        # Task legend
        task_legend = ctk.CTkLabel(
            legend_frame,
            text="📋 Tasks",
            fg_color=("#4A90E2", "#4A90E2"),
            text_color=("white", "white"),
            corner_radius=4,
            width=70,
            height=22,
            font=ctk.CTkFont(size=10)
        )
        task_legend.pack(side="left", padx=3)

        # Blocked legend
        blocked_legend = ctk.CTkLabel(
            legend_frame,
            text="🚫 Blocked",
            fg_color=("#FF6B6B", "#FF6B6B"),
            text_color=("white", "white"),
            corner_radius=4,
            width=70,
            height=22,
            font=ctk.CTkFont(size=10)
        )
        blocked_legend.pack(side="left", padx=3)

    def edit_timetable_cell(self, day, time_slot):
        """Opens a dialog to edit a timetable cell."""
        cell_key = f"{day}_{time_slot}"
        cell_data = self.timetable_data.get(cell_key, {})

        # Create edit window
        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Edit {day} {time_slot}")
        edit_window.geometry("500x700")
        edit_window.resizable(True, True)

        # Center window
        edit_window.transient(self)
        edit_window.grab_set()
        edit_window.update_idletasks()
        x = (self.winfo_x() + (self.winfo_width() // 2)) - (500 // 2)
        y = (self.winfo_y() + (self.winfo_height() // 2)) - (700 // 2)
        edit_window.geometry(f"500x700+{x}+{y}")

        # Configure grid for edit window
        edit_window.grid_columnconfigure(0, weight=1)
        edit_window.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            edit_window,
            text=f"📅 Edit {day} {time_slot}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")

        # Main scrollable container
        main_scroll = ctk.CTkScrollableFrame(
            edit_window, corner_radius=10)
        main_scroll.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        main_scroll.grid_columnconfigure(0, weight=1)

        # Type selection
        type_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        type_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(type_frame, text="Type:", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w")

        type_var = ctk.StringVar(value=cell_data.get('type', 'empty'))

        type_radio_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        type_radio_frame.pack(fill="x", pady=5)

        ctk.CTkRadioButton(type_radio_frame, text="Empty",
                           variable=type_var, value="empty").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_radio_frame, text="Lesson",
                           variable=type_var, value="lesson").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_radio_frame, text="Task",
                           variable=type_var, value="task").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_radio_frame, text="Blocked",
                           variable=type_var, value="blocked").pack(side="left", padx=10)

        # Lesson fields
        lesson_frame = ctk.CTkFrame(main_scroll)
        lesson_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(lesson_frame, text="Lesson Details:", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w", pady=(10, 5))

        # Module selection dropdown
        ctk.CTkLabel(lesson_frame, text="Module:").pack(anchor="w")
        module_var = ctk.StringVar(value=cell_data.get('module', ''))

        # Create dropdown first, then update values
        module_dropdown = ctk.CTkComboBox(
            lesson_frame,
            variable=module_var,
            dropdown_hover_color=("#1A3A47", "#1A3A47")
        )
        module_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        # Function to refresh module list in dropdown
        def refresh_module_dropdown():
            # Reload modules data to get any new modules
            self.modules_data = self.load_modules()
            # Get list of available modules
            module_names = list(self.modules_data.keys()
                                ) if self.modules_data else []
            module_dropdown.configure(values=module_names)
            return module_names

        # Initial load of modules
        available_modules = refresh_module_dropdown()

        # Refresh button for modules
        refresh_btn_frame = ctk.CTkFrame(lesson_frame, fg_color="transparent")
        refresh_btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        refresh_modules_btn = ctk.CTkButton(
            refresh_btn_frame,
            text="🔄 Refresh Modules",
            command=refresh_module_dropdown,
            fg_color=("#482728", "#482728"),
            hover_color=("#5A3233", "#5A3233"),
            font=ctk.CTkFont(size=10),
            height=25,
            width=120
        )
        refresh_modules_btn.pack(anchor="w")

        # Manual module entry (for new modules)
        ctk.CTkLabel(lesson_frame, text="Or enter new module:").pack(
            anchor="w")
        module_entry = ctk.CTkEntry(
            lesson_frame, placeholder_text="e.g., Mathematics")
        module_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Room selection - dynamic based on selected module
        ctk.CTkLabel(lesson_frame, text="Room:").pack(anchor="w")
        room_var = ctk.StringVar(value=cell_data.get('room', ''))

        room_dropdown = ctk.CTkComboBox(
            lesson_frame,
            variable=room_var,
            dropdown_hover_color=("#1A3A47", "#1A3A47")
        )
        room_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        # Function to update room options based on selected module
        def update_room_options():
            selected_module = module_var.get()
            if selected_module and selected_module in self.modules_data:
                module_rooms = self.modules_data[selected_module].get(
                    'rooms', ['Room Unknown'])
                room_dropdown.configure(values=module_rooms)
                # Auto-fill teacher if available
                module_teacher = self.modules_data[selected_module].get(
                    'teacher', '')
                if module_teacher:
                    teacher_entry.delete(0, 'end')
                    teacher_entry.insert(0, module_teacher)
            else:
                room_dropdown.configure(
                    values=['Room Unknown', 'Lab A', 'Lab B', 'Lecture Hall'])

        # Update room options when module selection changes
        def on_module_change(*args):
            update_room_options()

        module_var.trace('w', on_module_change)

        # Initial room options setup
        update_room_options()

        ctk.CTkLabel(lesson_frame, text="Teacher:").pack(anchor="w")
        teacher_entry = ctk.CTkEntry(
            lesson_frame, placeholder_text="e.g., Dr. Smith")
        teacher_entry.pack(fill="x", padx=10, pady=(0, 10))
        teacher_entry.insert(0, cell_data.get('teacher', ''))

        # Task fields
        task_frame = ctk.CTkFrame(main_scroll)
        task_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(task_frame, text="Task Details:", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(task_frame, text="Task Name:").pack(anchor="w")
        task_entry = ctk.CTkEntry(
            task_frame, placeholder_text="e.g., Study Session")
        task_entry.pack(fill="x", padx=10, pady=(0, 10))
        task_entry.insert(0, cell_data.get('task', ''))

        ctk.CTkLabel(task_frame, text="Description:").pack(anchor="w")
        task_desc_entry = ctk.CTkEntry(
            task_frame, placeholder_text="e.g., Prepare for exam")
        task_desc_entry.pack(fill="x", padx=10, pady=(0, 10))
        task_desc_entry.insert(0, cell_data.get('description', ''))

        # Buttons (outside scroll area)
        btn_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=20)

        def save_cell():
            cell_type = type_var.get()
            if cell_type == "empty":
                if cell_key in self.timetable_data:
                    del self.timetable_data[cell_key]
            else:
                # Get module name from dropdown or manual entry
                selected_module = module_var.get() if module_var.get() else module_entry.get()

                self.timetable_data[cell_key] = {
                    'type': cell_type,
                    'module': selected_module,
                    'room': room_var.get(),
                    'teacher': teacher_entry.get(),
                    'task': task_entry.get(),
                    'description': task_desc_entry.get()
                }

            self.save_timetable()
            edit_window.destroy()
            self.show_timetable()  # Refresh the timetable view

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=save_cell,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47")
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=edit_window.destroy,
            fg_color=("gray", "darkgray"),
            hover_color=("darkgray", "gray")
        )
        cancel_btn.pack(side="left", padx=10)

    def show_settings(self):
        """Shows the settings window for configuring storage location."""
        # Create settings window
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Calendar Pro Settings")
        settings_window.geometry("600x400")
        settings_window.resizable(True, True)

        # Center window
        settings_window.transient(self)
        settings_window.grab_set()
        settings_window.update_idletasks()
        x = (self.winfo_x() + (self.winfo_width() // 2)) - (600 // 2)
        y = (self.winfo_y() + (self.winfo_height() // 2)) - (400 // 2)
        settings_window.geometry(f"600x400+{x}+{y}")

        # Configure grid
        settings_window.grid_columnconfigure(0, weight=1)
        settings_window.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            settings_window,
            text="⚙️ Calendar Pro Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Main settings container
        settings_container = ctk.CTkFrame(settings_window, corner_radius=15)
        settings_container.grid(row=1, column=0, padx=20,
                                pady=(0, 10), sticky="nsew")
        settings_container.grid_columnconfigure(0, weight=1)

        # Storage location section
        storage_section = ctk.CTkFrame(
            settings_container, fg_color="transparent")
        storage_section.pack(fill="x", padx=20, pady=20)

        # Section title
        storage_title = ctk.CTkLabel(
            storage_section,
            text="📁 Data Storage Location",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        storage_title.pack(anchor="w", pady=(0, 10))

        # Description
        description_label = ctk.CTkLabel(
            storage_section,
            text="Choose where to store your notes, timetable, and modules data.\nSelect a OneDrive folder to sync between devices.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            justify="left"
        )
        description_label.pack(anchor="w", pady=(0, 15))

        # Current location display
        current_location_frame = ctk.CTkFrame(
            storage_section, fg_color=("gray95", "gray10"))
        current_location_frame.pack(fill="x", pady=(0, 15))

        current_label = ctk.CTkLabel(
            current_location_frame,
            text="Current Location:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        current_label.pack(anchor="w", padx=15, pady=(10, 5))

        current_path_label = ctk.CTkLabel(
            current_location_frame,
            text=load_storage_settings(),
            font=ctk.CTkFont(size=11),
            text_color=("gray20", "gray80"),
            wraplength=500
        )
        current_path_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(storage_section, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 10))

        # Change location button
        change_location_btn = ctk.CTkButton(
            buttons_frame,
            text="📂 Choose New Location",
            command=lambda: self.choose_storage_location(
                current_path_label, settings_window),
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40
        )
        change_location_btn.pack(side="left", padx=(0, 10))

        # Reset to default button
        reset_location_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset to Default",
            command=lambda: self.reset_storage_location(current_path_label),
            fg_color=("#482728", "#482728"),
            hover_color=("#5A3233", "#5A3233"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40
        )
        reset_location_btn.pack(side="left", padx=(0, 10))

        # Info section
        info_section = ctk.CTkFrame(
            settings_container, fg_color=("lightblue", "darkblue"))
        info_section.pack(fill="x", padx=20, pady=(0, 20))

        info_title = ctk.CTkLabel(
            info_section,
            text="💡 Tip: OneDrive Sync",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("white", "white")
        )
        info_title.pack(anchor="w", padx=15, pady=(10, 5))

        info_text = ctk.CTkLabel(
            info_section,
            text="To sync between devices:\n1. Choose a folder inside your OneDrive\n2. Install the app on other devices\n3. Set the same OneDrive folder on each device",
            font=ctk.CTkFont(size=11),
            text_color=("white", "white"),
            justify="left"
        )
        info_text.pack(anchor="w", padx=15, pady=(0, 10))

        # Close button
        close_btn_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
        close_btn_frame.grid(row=2, column=0, pady=20)

        close_btn = ctk.CTkButton(
            close_btn_frame,
            text="✅ Close",
            command=settings_window.destroy,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40
        )
        close_btn.pack()

    def choose_storage_location(self, path_label, window):
        """Opens a folder dialog to choose storage location."""
        current_location = load_storage_settings()
        new_location = filedialog.askdirectory(
            title="Choose Calendar Data Storage Location",
            initialdir=current_location
        )

        if new_location:
            # Save the new location
            save_storage_settings(new_location)
            self.storage_location = new_location

            # Update the display
            path_label.configure(text=new_location)

            # Show confirmation and reload data
            self.show_location_changed_message(window, new_location)
            self.reload_data_from_new_location()

    def reset_storage_location(self, path_label):
        """Resets storage location to default OneDrive location."""
        default_location = r"C:\Users\umfhe\OneDrive - Middlesex University\A - Calendar Pro"
        # Create the default directory if it doesn't exist
        if not os.path.exists(default_location):
            try:
                os.makedirs(default_location, exist_ok=True)
            except:
                # If we can't create the OneDrive folder, fall back to current directory
                default_location = os.getcwd()

        save_storage_settings(default_location)
        self.storage_location = default_location
        path_label.configure(text=default_location)
        self.reload_data_from_new_location()

    def reload_data_from_new_location(self):
        """Reloads all data from the new storage location and refreshes UI."""
        # Reload all data files
        self.note_data = self.load_notes()
        self.timetable_data = self.load_timetable()
        self.modules_data = self.load_modules()

        # Add preset module if no modules exist in new location
        if not self.modules_data:
            self.modules_data = {
                "CST3510 Memory Analysis": {
                    "color": "#45B7D1",
                    "teacher": "Mr David Neilson",
                    "rooms": ["Room Unknown", "Lab A", "Lab B", "Lecture Hall 1", "Lecture Hall 2"],
                    "created": datetime.now().isoformat()
                }
            }
            self.save_modules()

        # Refresh the UI
        self.refresh_month_notifications()

        # Return to home view to show updated data
        self.show_months_list()

    def refresh_month_notifications(self):
        """Refreshes the notification counters for all months."""
        current_year = datetime.now().year

        # Clear existing notification labels
        for month_name, canvas in self.month_note_labels.items():
            if canvas:
                canvas.destroy()

        # Recreate the month list with updated data
        for widget in self.left_frame.winfo_children():
            # Month buttons start at row 3
            if hasattr(widget, 'grid_info') and widget.grid_info()['row'] >= 3:
                widget.destroy()

        self.month_buttons = {}
        self.month_note_labels = {}
        self.create_month_list()

    def show_location_changed_message(self, parent_window, new_location):
        """Shows a message about location change and data migration."""
        # Create message window
        msg_window = ctk.CTkToplevel(parent_window)
        msg_window.title("Location Changed")
        msg_window.geometry("500x300")
        msg_window.resizable(False, False)

        # Center on parent
        msg_window.transient(parent_window)
        msg_window.grab_set()
        parent_window.update_idletasks()
        x = (parent_window.winfo_x() +
             (parent_window.winfo_width() // 2)) - (500 // 2)
        y = (parent_window.winfo_y() +
             (parent_window.winfo_height() // 2)) - (300 // 2)
        msg_window.geometry(f"500x300+{x}+{y}")

        # Configure grid
        msg_window.grid_columnconfigure(0, weight=1)
        msg_window.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            msg_window,
            text="✅ Storage Location Updated",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Message content
        content_frame = ctk.CTkFrame(msg_window, corner_radius=15)
        content_frame.grid(row=1, column=0, padx=20,
                           pady=(0, 10), sticky="nsew")

        message_text = f"""Storage location changed to:
{new_location}

Your existing data files will remain in the old location.

To move your data to the new location:
• Copy notes.json, timetable.json, and modules.json
• From the old location to: {new_location}

The app will create new files if none exist in the new location."""

        message_label = ctk.CTkLabel(
            content_frame,
            text=message_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=450
        )
        message_label.pack(padx=20, pady=20)

        # Close button
        close_btn = ctk.CTkButton(
            msg_window,
            text="OK",
            command=msg_window.destroy,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47"),
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40
        )
        close_btn.grid(row=2, column=0, pady=20)

    def show_modules_manager(self):
        """Shows the module management window."""
        # Create modules manager window
        modules_window = ctk.CTkToplevel(self)
        modules_window.title("Manage Modules")
        modules_window.geometry("600x500")
        modules_window.resizable(True, True)

        # Center window
        modules_window.transient(self)
        modules_window.grab_set()
        modules_window.update_idletasks()
        x = (self.winfo_x() + (self.winfo_width() // 2)) - (600 // 2)
        y = (self.winfo_y() + (self.winfo_height() // 2)) - (500 // 2)
        modules_window.geometry(f"600x500+{x}+{y}")

        # Configure grid
        modules_window.grid_columnconfigure(0, weight=1)
        modules_window.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            modules_window,
            text="📚 Module Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))

        # Main container
        main_container = ctk.CTkFrame(modules_window)
        main_container.grid(row=1, column=0, padx=20,
                            pady=(0, 20), sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for modules list
        modules_scroll = ctk.CTkScrollableFrame(main_container)
        modules_scroll.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add new module section
        new_module_frame = ctk.CTkFrame(modules_scroll)
        new_module_frame.pack(fill="x", padx=10, pady=(10, 20))

        ctk.CTkLabel(
            new_module_frame,
            text="Add New Module",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Module name entry
        name_frame = ctk.CTkFrame(new_module_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(name_frame, text="Module Name:").pack(anchor="w")
        module_name_entry = ctk.CTkEntry(
            name_frame, placeholder_text="e.g., CST3510 Memory Analysis"
        )
        module_name_entry.pack(fill="x", pady=(0, 10))

        # Teacher entry
        teacher_frame = ctk.CTkFrame(new_module_frame, fg_color="transparent")
        teacher_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(teacher_frame, text="Teacher/Lecturer:").pack(anchor="w")
        teacher_entry = ctk.CTkEntry(
            teacher_frame, placeholder_text="e.g., Mr David Neilson"
        )
        teacher_entry.pack(fill="x", pady=(0, 10))

        # Rooms entry
        rooms_frame = ctk.CTkFrame(new_module_frame, fg_color="transparent")
        rooms_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            rooms_frame, text="Possible Rooms (comma-separated):").pack(anchor="w")
        rooms_entry = ctk.CTkEntry(
            rooms_frame, placeholder_text="e.g., Lab A, Lab B, Lecture Hall 1"
        )
        rooms_entry.pack(fill="x", pady=(0, 10))

        # Color selection
        color_frame = ctk.CTkFrame(new_module_frame, fg_color="transparent")
        color_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(color_frame, text="Module Color:").pack(anchor="w")

        # Color selection buttons
        color_options = [
            ("#FF6B6B", "Red"),
            ("#4ECDC4", "Teal"),
            ("#45B7D1", "Blue"),
            ("#96CEB4", "Green"),
            ("#FFEAA7", "Yellow"),
            ("#DDA0DD", "Purple"),
            ("#FFB347", "Orange"),
            ("#98D8C8", "Mint"),
            ("#F7DC6F", "Gold"),
            ("#BB8FCE", "Lavender")
        ]

        selected_color = ctk.StringVar(value=color_options[0][0])
        color_buttons = []  # Keep track of color buttons for highlighting

        colors_container = ctk.CTkFrame(color_frame, fg_color="transparent")
        colors_container.pack(fill="x", pady=(0, 10))

        def update_color_selection(new_color):
            selected_color.set(new_color)
            # Update button appearances
            for btn, (hex_color, _) in zip(color_buttons, color_options):
                if hex_color == new_color:
                    btn.configure(border_width=3, border_color="white")
                else:
                    btn.configure(border_width=0)
            # Update preview
            update_preview()

        for i, (color_hex, color_name) in enumerate(color_options):
            row = i // 5
            col = i % 5

            color_btn = ctk.CTkButton(
                colors_container,
                text="",
                width=40,
                height=30,
                fg_color=color_hex,
                hover_color=color_hex,
                border_width=3 if i == 0 else 0,  # Highlight first color initially
                border_color="white" if i == 0 else None,
                command=lambda c=color_hex: update_color_selection(c)
            )
            color_btn.grid(row=row, column=col, padx=2, pady=2)
            color_buttons.append(color_btn)

        # Preview frame
        preview_frame = ctk.CTkFrame(color_frame, fg_color="transparent")
        preview_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(preview_frame, text="Preview:").pack(anchor="w")

        preview_container = ctk.CTkFrame(preview_frame)
        preview_container.pack(fill="x", pady=(5, 0))

        preview_label = ctk.CTkLabel(
            preview_container,
            text="Sample Module",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=selected_color.get(),
            text_color="white",
            corner_radius=6,
            height=35
        )
        preview_label.pack(padx=10, pady=10, fill="x")

        def update_preview():
            module_name = module_name_entry.get().strip() or "Sample Module"
            preview_label.configure(
                text=module_name,
                fg_color=selected_color.get()
            )

        # Update preview when module name changes
        def on_name_change(*args):
            update_preview()

        module_name_entry.bind('<KeyRelease>', on_name_change)
        teacher_entry.bind('<KeyRelease>', on_name_change)
        rooms_entry.bind('<KeyRelease>', on_name_change)

        # Add button
        def add_module():
            name = module_name_entry.get().strip()
            teacher = teacher_entry.get().strip() or "Unknown"
            rooms_text = rooms_entry.get().strip()
            rooms_list = [room.strip() for room in rooms_text.split(
                ',') if room.strip()] if rooms_text else ["Room Unknown"]

            if name and name not in self.modules_data:
                self.modules_data[name] = {
                    'color': selected_color.get(),
                    'teacher': teacher,
                    'rooms': rooms_list,
                    'created': datetime.now().isoformat()
                }
                self.save_modules()
                # Debug output
                print(
                    f"Module '{name}' saved with color {selected_color.get()}")
                print(f"Teacher: {teacher}")
                print(f"Rooms: {rooms_list}")
                print(f"Total modules: {len(self.modules_data)}")
                # Clear the form
                module_name_entry.delete(0, 'end')
                teacher_entry.delete(0, 'end')
                rooms_entry.delete(0, 'end')
                # Reset to first color
                update_color_selection(color_options[0][0])
                # Show success message
                success_label = ctk.CTkLabel(
                    new_module_frame,
                    text="✅ Module added successfully!",
                    text_color="#0B2027",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                success_label.pack(pady=5)
                modules_window.after(2000, success_label.destroy)
                # Refresh the existing modules section
                refresh_existing_modules()
            elif not name:
                # Show error message for empty name
                error_label = ctk.CTkLabel(
                    new_module_frame,
                    text="❌ Please enter a module name!",
                    text_color="red",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                error_label.pack(pady=5)
                modules_window.after(2000, error_label.destroy)
            elif name in self.modules_data:
                # Show error message for duplicate
                error_label = ctk.CTkLabel(
                    new_module_frame,
                    text="❌ Module already exists!",
                    text_color="red",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                error_label.pack(pady=5)
                modules_window.after(2000, error_label.destroy)

        add_btn = ctk.CTkButton(
            new_module_frame,
            text="💾 Save Module",
            command=add_module,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35
        )
        add_btn.pack(pady=(10, 15))

        # Function to refresh existing modules display
        def refresh_existing_modules():
            # Clear existing modules display
            for widget in modules_scroll.winfo_children():
                if widget != new_module_frame:
                    widget.destroy()

            # Recreate existing modules section
            if self.modules_data:
                existing_frame = ctk.CTkFrame(modules_scroll)
                existing_frame.pack(fill="x", padx=10, pady=10)

                ctk.CTkLabel(
                    existing_frame,
                    text="Existing Modules",
                    font=ctk.CTkFont(size=18, weight="bold")
                ).pack(pady=(15, 10))

                for module_name, module_info in self.modules_data.items():
                    module_item = ctk.CTkFrame(existing_frame)
                    module_item.pack(fill="x", padx=15, pady=5)

                    # Module info frame
                    info_frame = ctk.CTkFrame(
                        module_item, fg_color="transparent")
                    info_frame.pack(fill="x", side="left", expand=True)

                    # Color indicator
                    color_indicator = ctk.CTkLabel(
                        info_frame,
                        text="●",
                        font=ctk.CTkFont(size=20),
                        text_color=module_info['color']
                    )
                    color_indicator.pack(side="left", padx=(10, 5))

                    # Module details frame
                    details_frame = ctk.CTkFrame(
                        info_frame, fg_color="transparent")
                    details_frame.pack(side="left", fill="x",
                                       expand=True, padx=(0, 10))

                    # Module name
                    name_label = ctk.CTkLabel(
                        details_frame,
                        text=module_name,
                        font=ctk.CTkFont(size=14, weight="bold"),
                        anchor="w"
                    )
                    name_label.pack(anchor="w")

                    # Teacher info
                    teacher = module_info.get('teacher', 'Unknown')
                    teacher_label = ctk.CTkLabel(
                        details_frame,
                        text=f"👨‍🏫 {teacher}",
                        font=ctk.CTkFont(size=11),
                        text_color=("gray40", "gray60"),
                        anchor="w"
                    )
                    teacher_label.pack(anchor="w")

                    # Rooms info
                    rooms = module_info.get('rooms', ['Room Unknown'])
                    rooms_text = ", ".join(rooms)
                    if len(rooms_text) > 35:
                        rooms_text = rooms_text[:32] + "..."
                    rooms_label = ctk.CTkLabel(
                        details_frame,
                        text=f"🏛️ {rooms_text}",
                        font=ctk.CTkFont(size=11),
                        text_color=("gray40", "gray60"),
                        anchor="w"
                    )
                    rooms_label.pack(anchor="w")

                    # Delete button
                    def delete_module(name=module_name):
                        del self.modules_data[name]
                        self.save_modules()
                        refresh_existing_modules()  # Refresh instead of destroying window

                    delete_btn = ctk.CTkButton(
                        module_item,
                        text="🗑️",
                        width=30,
                        height=30,
                        command=delete_module,
                        fg_color=("red", "darkred"),
                        hover_color=("darkred", "red")
                    )
                    delete_btn.pack(side="right", padx=10, pady=5)

        # Initial display of existing modules
        refresh_existing_modules()

        # Close button
        close_btn = ctk.CTkButton(
            modules_window,
            text="✓ Done",
            command=modules_window.destroy,
            fg_color=("#0B2027", "#0B2027"),
            hover_color=("#1A3A47", "#1A3A47")
        )
        close_btn.grid(row=2, column=0, pady=10)

    def update_month_notification(self, month_name, note_count):
        """Updates the notification for a specific month."""
        # Find the month number for the month name
        month_num = list(calendar.month_name).index(month_name)

        # Remove existing notification if any
        existing_notification = self.month_note_labels.get(month_name)
        if existing_notification:
            existing_notification.master.destroy()  # Destroy the entire notification frame
            self.month_note_labels[month_name] = None

        # Create new notification if there are notes
        if note_count > 0:
            # Create notification frame outside the button container
            notification_frame = ctk.CTkFrame(
                self.left_frame, fg_color="transparent")
            notification_frame.grid(
                row=month_num+2, column=1, padx=(5, 15), pady=2, sticky="ne")

            # Try using Canvas to overlay text on image without background
            import tkinter as tk
            canvas = tk.Canvas(
                notification_frame,
                width=42,
                height=42,
                highlightthickness=0,
                bg='#dbdbdb'  # Use the exact background color you mentioned
            )
            canvas.pack()

            # Load and draw the icon image on canvas
            try:
                from PIL import ImageTk
                icon_pil = Image.open(resource_path(
                    "bell.png")).resize((42, 42))
                icon_photo = ImageTk.PhotoImage(icon_pil)
                canvas.create_image(21, 21, image=icon_photo)
                # Keep a reference to prevent garbage collection
                canvas.image = icon_photo

                # Draw text with black color (no background circle)
                canvas.create_text(21, 21, text=str(note_count),
                                   font=("Arial", 14, "bold"),
                                   fill="black")
            except Exception as e:
                # Fallback to simple colored circle with text
                canvas.create_oval(5, 5, 37, 37, fill="red",
                                   outline="white", width=2)
                canvas.create_text(21, 21, text=str(note_count),
                                   font=("Arial", 16, "bold"),
                                   fill="white")

            # Store the canvas for future updates
            self.month_note_labels[month_name] = canvas

    def enter_delete_mode(self):
        """Enters delete mode for mass note deletion."""
        self.delete_mode = True
        self.selected_days = set()
        # Refresh the calendar to show delete mode UI
        self.show_calendar(self.current_month)

    def exit_delete_mode(self):
        """Exits delete mode and returns to normal calendar view."""
        self.delete_mode = False
        self.selected_days = set()
        # Refresh the calendar to show normal UI
        self.show_calendar(self.current_month)

    def toggle_day_selection(self, day, year, month_name):
        """Toggles selection of a day for deletion (only if it has notes)."""
        # Only allow selection of days that have notes
        day_notes = self.note_data.get(str(year), {}).get(
            month_name, {}).get(str(day), [])
        if day_notes:  # Only select days that have notes
            if day in self.selected_days:
                self.selected_days.remove(day)
            else:
                self.selected_days.add(day)
            # Refresh the calendar to update selection display
            self.show_calendar(self.current_month)

    def confirm_delete_selected(self):
        """Confirms and deletes notes for all selected days."""
        if not self.selected_days:
            return

        # Create confirmation dialog
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirm Deletion")
        confirm_window.geometry("450x300")
        confirm_window.resizable(False, False)

        # Center the window and make it modal
        confirm_window.transient(self)
        confirm_window.grab_set()

        # Center window on parent
        confirm_window.update_idletasks()
        x = (self.winfo_x() + (self.winfo_width() // 2)) - (450 // 2)
        y = (self.winfo_y() + (self.winfo_height() // 2)) - (300 // 2)
        confirm_window.geometry(f"450x300+{x}+{y}")

        # Main container
        main_frame = ctk.CTkFrame(confirm_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning icon and title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="⚠️ Confirm Deletion",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("red", "red")
        )
        title_label.pack()

        # Message container
        message_frame = ctk.CTkFrame(
            main_frame, corner_radius=10, fg_color=("gray95", "gray10"))
        message_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Get details
        current_year = datetime.now().year
        month_name = calendar.month_name[self.current_month]
        selected_count = len(self.selected_days)

        # Main message
        main_msg = ctk.CTkLabel(
            message_frame,
            text=f"Delete notes for {selected_count} day{'s' if selected_count != 1 else ''}?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0B2027", "#0B2027")
        )
        main_msg.pack(pady=(20, 10))

        # Details
        details_msg = ctk.CTkLabel(
            message_frame,
            text=f"Month: {month_name} {current_year}",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        details_msg.pack(pady=5)

        # Days list
        days_text = f"Days: {', '.join(map(str, sorted(self.selected_days)))}"
        days_msg = ctk.CTkLabel(
            message_frame,
            text=days_text,
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        days_msg.pack(pady=5)

        # Warning
        warning_msg = ctk.CTkLabel(
            message_frame,
            text="This action cannot be undone!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("red", "red")
        )
        warning_msg.pack(pady=(10, 20))

        # Button frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        # Delete button
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete All",
            command=lambda: self.execute_deletion(confirm_window),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            height=40,
            width=150
        )
        delete_btn.pack(side="left", padx=(0, 10))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=confirm_window.destroy,
            fg_color=("gray", "darkgray"),
            hover_color=("darkgray", "gray"),
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            height=40,
            width=150
        )
        cancel_btn.pack(side="right", padx=(10, 0))

    def execute_deletion(self, confirm_window):
        """Executes the deletion of selected days' notes."""
        current_year = datetime.now().year
        month_name = calendar.month_name[self.current_month]
        year_str = str(current_year)

        # Delete notes for selected days
        if year_str in self.note_data and month_name in self.note_data[year_str]:
            for day in self.selected_days:
                day_str = str(day)
                if day_str in self.note_data[year_str][month_name]:
                    del self.note_data[year_str][month_name][day_str]

        # Save updated data
        notes_file_path = get_data_file_path('notes.json')
        with open(notes_file_path, 'w') as f:
            json.dump(self.note_data, f, indent=4)

        # Update the month counter
        note_count = len(
            [day for day, notes in self.note_data.get(year_str, {}).get(month_name, {}).items() if notes])
        self.update_month_notification(month_name, note_count)

        # Close confirmation window
        confirm_window.destroy()

        # Exit delete mode and refresh calendar
        self.exit_delete_mode()

    def update_month_counters(self):
        """Updates all month note counters on the left panel."""
        current_year = datetime.now().year

        for month_name in calendar.month_name[1:]:
            month_data = self.note_data.get(
                str(current_year), {}).get(month_name, {})
            note_count = len(
                [day for day, notes in month_data.items() if notes])

            self.update_month_notification(month_name, note_count)


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
