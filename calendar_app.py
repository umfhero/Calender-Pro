import customtkinter as ctk
import calendar
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from PIL import Image

# Configure the appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


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

        # Set app icon
        try:
            self.iconbitmap("calendar.ico")
        except:
            pass  # Continue without icon if file not found

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load existing notes
        self.note_data = self.load_notes()
        self.current_month = None
        self.delete_mode = False
        self.selected_days = set()  # Track selected days for deletion

        # Create the main layout
        self.create_left_panel()
        self.create_right_panel()

        # Initialize with welcome message and highlight current month
        self.show_months_list()

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
        self.left_frame.grid_rowconfigure(13, weight=1)

        # Home button at the top
        home_btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        home_btn_frame.grid(row=0, column=0, padx=15,
                            pady=(10, 5), sticky="ew")

        # Load home icon
        home_icon = None
        try:
            home_icon = ctk.CTkImage(
                light_image=Image.open("house.ico"),
                dark_image=Image.open("house.ico"),
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

            # Create button container with rounded corners
            btn_container = ctk.CTkFrame(
                self.left_frame, corner_radius=12, fg_color="transparent")
            btn_container.grid(row=i, column=0, padx=15, pady=2, sticky="ew")

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
                    row=i, column=1, padx=(5, 15), pady=2, sticky="ne")

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
                    icon_pil = Image.open("icon.png").resize((45, 45))
                    icon_photo = ImageTk.PhotoImage(icon_pil)
                    canvas.create_image(21, 21, image=icon_photo)
                    # Keep a reference to prevent garbage collection
                    canvas.image = icon_photo

                    # Draw text directly on canvas
                    canvas.create_text(21, 21, text=str(note_count),
                                       font=("Arial", 16, "bold"),
                                       fill="black")
                except:
                    # Fallback to simple colored circle with text
                    canvas.create_oval(5, 5, 37, 37, fill="red", outline="")
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
                fg_color = ("#482728", "#482728")
                hover_color = ("#5A3233", "#5A3233")
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
                light_image=Image.open("house.ico"),
                dark_image=Image.open("house.ico"),
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
                        light_image=Image.open("edit.png"),
                        dark_image=Image.open("edit.png"),
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
        with open('notes.json', 'w') as f:
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
        if os.path.exists('notes.json'):
            try:
                with open('notes.json', 'r') as f:
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
        with open('notes.json', 'w') as f:
            json.dump(self.note_data, f, indent=4)

        # Update the month counter on the left panel
        note_count = len(
            [day for day, notes in self.note_data[year_str][month_name].items() if notes])
        self.update_month_notification(month_name, note_count)

        # Close the window
        window.destroy()

        # Show success message
        self.show_success_message()

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
                row=month_num, column=1, padx=(5, 15), pady=2, sticky="ne")

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
                icon_pil = Image.open("icon.png").resize((42, 42))
                icon_photo = ImageTk.PhotoImage(icon_pil)
                canvas.create_image(21, 21, image=icon_photo)
                # Keep a reference to prevent garbage collection
                canvas.image = icon_photo

                # Draw text directly on canvas
                canvas.create_text(21, 21, text=str(note_count),
                                   font=("Arial", 16, "bold"),
                                   fill="black")
            except:
                # Fallback to simple colored circle with text
                canvas.create_oval(5, 5, 37, 37, fill="red", outline="")
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
        with open('notes.json', 'w') as f:
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
