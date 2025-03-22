from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar
from dataclasses import dataclass
from datetime import date
import customtkinter as ctk
import random

class Agenda(Calendar):
    """
    An overload of the tkcalendar.Calendar class to display events as text in the calendar instead of tooltips.
    Found on StackOverflow: https://stackoverflow.com/questions/64107018/is-it-possible-to-embed-custom-text-in-python-tkcalendars-date
    """

    def __init__(self, master=None, **kw):
        Calendar.__init__(self, master, **kw)
        # change a bit the options of the labels to improve display
        for i, row in enumerate(self._calendar):
            for j, label in enumerate(row):
                self._cal_frame.rowconfigure(i + 1, uniform=1)
                self._cal_frame.columnconfigure(j + 1, uniform=1)
                label.configure(justify="center", anchor="n", padding=(1, 4))

    def _display_days_without_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdays2calendar(year, month)
        while len(cal) < 6:
            cal.append([(0, i) for i in range(7)])

        week_days = {i: 'normal.%s.TLabel' % self._style_prefixe for i in range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we.%s.TLabel' % self._style_prefixe
        week_days[self['weekenddays'][1] - 1] = 'we.%s.TLabel' % self._style_prefixe
        _, week_nb, d = self._date.isocalendar()
        if d == 7 and self['firstweekday'] == 'sunday':
            week_nb += 1
        modulo = max(week_nb, 52)
        for i_week in range(6):
            if i_week == 0 or cal[i_week][0][0]:
                self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            else:
                self._week_nbs[i_week].configure(text='')
            for i_day in range(7):
                day_number, week_day = cal[i_week][i_day]
                style = week_days[i_day]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                if day_number:
                    txt = str(day_number)
                    label.configure(text=txt, style=style)
                    date = self.date(year, month, day_number)
                    if date in self._calevent_dates:
                        ev_ids = self._calevent_dates[date]
                        i = len(ev_ids) - 1
                        while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                            i -= 1
                        if i >= 0:
                            tag = self.calevents[ev_ids[i]]['tags'][-1]
                            label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                        # modified lines:
                        text = '%s\n' % day_number + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])
                        label.configure(text=text)
                else:
                    label.configure(text='', style=style)

    def _display_days_with_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdatescalendar(year, month)

        next_m = month + 1
        y = year
        if next_m == 13:
            next_m = 1
            y += 1
        if len(cal) < 6:
            if cal[-1][-1].month == month:
                i = 0
            else:
                i = 1
            cal.append(self._cal.monthdatescalendar(y, next_m)[i])
            if len(cal) < 6:
                cal.append(self._cal.monthdatescalendar(y, next_m)[i + 1])

        week_days = {i: 'normal' for i in range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we'
        week_days[self['weekenddays'][1] - 1] = 'we'
        prev_m = (month - 2) % 12 + 1
        months = {month: '.%s.TLabel' % self._style_prefixe,
                  next_m: '_om.%s.TLabel' % self._style_prefixe,
                  prev_m: '_om.%s.TLabel' % self._style_prefixe}

        week_nb = cal[0][1].isocalendar()[1]
        modulo = max(week_nb, 52)
        for i_week in range(6):
            self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            for i_day in range(7):
                style = week_days[i_day] + months[cal[i_week][i_day].month]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                txt = str(cal[i_week][i_day].day)
                label.configure(text=txt, style=style)
                if cal[i_week][i_day] in self._calevent_dates:
                    date = cal[i_week][i_day]
                    ev_ids = self._calevent_dates[date]
                    i = len(ev_ids) - 1
                    while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                        i -= 1
                    if i >= 0:
                        tag = self.calevents[ev_ids[i]]['tags'][-1]
                        label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                    # modified lines:
                    text = '%s\n' % date.day + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])
                    label.configure(text=text)

    def _show_event(self, date):
        """Display events on date if visible."""
        w, d = self._get_day_coords(date)
        if w is not None:
            label = self._calendar[w][d]
            if not label.cget('text'):
                # this is an other month's day and showothermonth is False
                return
            ev_ids = self._calevent_dates[date]
            i = len(ev_ids) - 1
            while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                i -= 1
            if i >= 0:
                tag = self.calevents[ev_ids[i]]['tags'][-1]
                label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
            # modified lines:
            text = '%s\n' % date.day + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])
            label.configure(text=text)

@dataclass
class Event:
    """
    A class representing an event.

    :ivar day: The day of the event.
    :ivar month: The month of the event.
    :ivar year: The year of the event.
    :ivar title: The title of the event.
    :ivar type: The type of the event (e.g., Exam, Homework, Quiz).
    """
    day: int
    month: int
    year: int
    title: str
    type: str


class BestCalendar(Agenda):
    """
    A custom calendar class for managing events.

    :ivar _is_event_triggered: A flag indicating whether an event is triggered.
    :ivar _events: A list of events stored as tuples of event IDs and Event objects.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the calendar.

        :param args: Positional arguments for the parent class.
        :param kwargs: Keyword arguments for the parent class.
        """
        super().__init__(*args, **kwargs)
        self._is_event_triggered = False
        self._events = []

        # Configure tags for event types
        self.tag_config("Exam", background="red", foreground="white")
        self.tag_config("Quiz", background="yellow", foreground="black")
        self.tag_config("Homework", background="blue", foreground="white")

    def add_event(self, event: Event):
        """
        Add an event to the calendar.

        :param event: The Event object to add.
        """
        event_id = self.calevent_create(date(event.year, event.month, event.day), event.title, tags=event.type)
        self._events.append((event_id, event))

    def get_selected_date(self):
        """
        Get the currently selected date in the calendar.

        :return: The selected date as a string.
        """
        return self.get_date()

    def get_events(self):
        """
        Get all the events.

        :return: All the events as a list of Event objects.
        """
        return self._events

class App(ctk.CTk):
    """
    The main application class for the calendar app.

    :ivar frame: The main frame of the application.
    :ivar calendar: The custom calendar widget.
    :ivar event_window: The window for adding events.
    :ivar title_entry: The entry widget for the event title.
    :ivar event_type: The variable for the event type dropdown.
    :ivar type_dropdown: The dropdown menu for selecting event types.
    :ivar reminder_window: The window for managing reminders.
    :ivar reminders_list: The list of reminders.
    :ivar reminder_present: The label displaying reminders.
    :ivar selected_date: The currently selected date in the calendar.
    :ivar sidebar: The sidebar with buttons for tasks, reminders, and quotes.
    :ivar title_entry: The entry widget for the event title.
    :ivar type_dropdown: The dropdown menu for selecting event types.
    """

    def __init__(self):
        """
        Initialize the application.
        """
        super().__init__()
        self.title("Best Calendar")
        self.geometry("700x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Initialize instance variables
        self.frame = None
        self.calendar = None
        self.event_window = None
        self.title_entry = None
        self.event_type = None
        self.type_dropdown = None
        self.reminder_window = None
        self.reminders_list = []
        self.reminder_present = None
        self.selected_date = None
        self.sidebar = None
        self.title_entry = None
        self.type_dropdown = None

        # Set up the main frame
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)

        # Create the calendar
        self.calendar = BestCalendar(
            self.frame,
            year=2025,
            month=3,
            day=22,
            font="Modern 14",
            locale="en_US",
            disabledforeground="red",
            cursor="hand2",
            background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
            selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1],
        )
        self.calendar.pack(fill="both", expand=True, pady=20)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_click)

        # Create the sidebar
        self._create_sidebar()

    def _create_sidebar(self):
        """Create the sidebar with buttons for tasks, reminders, and quotes."""
        self.sidebar = ctk.CTkFrame(self.frame, height=100)
        self.sidebar.pack(side="bottom", fill="x", expand=False)

        # Configure grid layout for the sidebar
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(2, weight=1)

        # Task button
        ctk.CTkButton(
            self.sidebar,
            text="Tasks",
            command=self.tasks,
            fg_color="#a47864",
            hover_color="#815947",
            text_color="black",
            font=("Modern", 14, "bold"),
            corner_radius=0,
        ).grid(row=0, column=0, sticky="nsew")

        # Reminder button
        ctk.CTkButton(
            self.sidebar,
            text="Reminders",
            command=self.reminders,
            fg_color="#a47864",
            hover_color="#815947",
            text_color="black",
            font=("Modern", 14, "bold"),
            corner_radius=0,
        ).grid(row=0, column=1, sticky="nsew")

        # Quote button
        ctk.CTkButton(
            self.sidebar,
            text="Quote of the Day",
            command=self.quote,
            fg_color="#a47864",
            hover_color="#815947",
            text_color="black",
            font=("Modern", 14, "bold"),
            corner_radius=0,
        ).grid(row=0, column=2, sticky="nsew")

    def submit_event(self):
        """
        Submit a new event to the calendar.
        """
        try:
            title = self.title_entry.get()
            event_type_value = self.event_type.get()
            if not title:
                messagebox.showerror("Error", "Event title cannot be empty!")
                return

            # Ensure selected_date is in MM/DD/YY format
            if not self.selected_date:
                messagebox.showerror("Error", "No date selected!")
                return

            month, day, year = map(int, self.selected_date.split('/'))
            year += 2000  # Convert 2-digit year to 4-digit year

            # Create and add the event
            new_event = Event(day, month, year, title, event_type_value)
            self.calendar.add_event(new_event)
            self.event_window.destroy()  # Close the event window
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")

    def on_date_click(self, event):
        """
        Handle the event when a date is clicked in the calendar.

        :param event: The event object triggered by the click.
        """
        self.selected_date = self.calendar.get_selected_date()
        self.open_event_menu()

    def open_event_menu(self):
        """Open the event menu for adding a new event."""
        self.event_window = ctk.CTkToplevel(self)
        self.event_window.title("Add Event")
        self.event_window.geometry("300x250")

        # Event title input
        ctk.CTkLabel(self.event_window, text="Event Title:").pack(pady=5)
        self.title_entry = ctk.CTkEntry(self.event_window)
        self.title_entry.pack(pady=5)

        # Event type dropdown
        ctk.CTkLabel(self.event_window, text="Event Type:").pack(pady=5)
        self.event_type = StringVar(self.event_window)
        self.event_type.set("Exam") # Default value
        self.type_dropdown = ctk.CTkOptionMenu(
            self.event_window,
            variable=self.event_type,
            values=["Exam", "Quiz", "Homework"],
        )
        self.type_dropdown.pack(pady=5)

        # Submit button
        ctk.CTkButton(
            self.event_window,
            text="Add Event",
            command=self.submit_event,
            fg_color="blue",
            hover_color="darkblue",
            text_color="white",
        ).pack(pady=30)

    def tasks(self):
        """Display all events in a new window, sorted by closest date."""
        task_window = ctk.CTkToplevel(self)
        task_window.title("Upcoming Tasks")
        task_window.geometry("300x400")

        # Retrieve and sort events by date
        events = self.calendar.get_events()
        sorted_events = sorted(events, key=lambda e: date(e[1].year, e[1].month, e[1].day)) # Sort by event date

        # Format the events for display
        if sorted_events:
            event_text = "\n\n".join(
                f"Name: {event.title}\nDate: {event.month}/{event.day}/{event.year}\n ---" for _, event in sorted_events
            )
        else:
            event_text = "No events available."

        # Display the events in the task window
        ctk.CTkLabel(
            task_window,
            text=event_text,
            font=("Modern", 16),
            wraplength=250,
            justify="center",
        ).pack(pady=20)

    def quote(self):
        """Display a random motivational quote in a new window."""
        quotes = [
            "\"100s only\"", "\"You got this\"", "\"One step at a time\"",
            "\"Lock in\"", "\"Think about the money\"", "\"Get that degree\"", "\"Suffer now, spend later\""
        ]
        quote = random.choice(quotes)

        quote_window = ctk.CTkToplevel(self)
        quote_window.title("Quote of the Day!")
        quote_window.geometry("300x100")
        ctk.CTkLabel(quote_window, text=quote, font=("Modern", 20), wraplength=250).pack(pady=20)

    def reminders(self):
        """Open the reminders window to manage reminders."""
        if self.reminder_window and self.reminder_window.winfo_exists():
            self.reminder_window.lift()
            return

        self.reminder_window = ctk.CTkToplevel(self)
        self.reminder_window.title("Reminders")
        self.reminder_window.geometry("300x200")

        # Display reminders or show "No reminders yet" if the list is empty
        self.reminder_present = ctk.CTkLabel(
            self.reminder_window,
            text="\n".join(self.reminders_list) if self.reminders_list else "No reminders yet",
            justify="left", font=("Modern", 16),
        )
        self.reminder_present.pack(pady=10)

        # Add Reminder button
        ctk.CTkButton(
            self.reminder_window,
            text="Add Reminder",
            command=self.add_reminder,
        ).pack(pady=10)

        # Remove Reminder button
        ctk.CTkButton(
            self.reminder_window,
            text="Remove Reminder",
            command=self.remove_reminder,
            fg_color="red",
            hover_color="darkred",
            text_color="white",
        ).pack(pady=10)

    def add_reminder(self):
        """Open a window to add a new reminder."""
        add_reminder_window = ctk.CTkToplevel(self)
        add_reminder_window.title("Add Reminder")
        add_reminder_window.geometry("300x150")

        ctk.CTkLabel(add_reminder_window, text="Enter Reminder:").pack(pady=5)
        reminder_entry = ctk.CTkEntry(add_reminder_window, width=200)
        reminder_entry.pack(pady=5)

        def save_reminder():
            """Save the entered reminder."""
            text = reminder_entry.get().strip()
            if text:
                self.reminders_list.append(text) # Add the reminder to the list
                self.reminder_present.configure(text="\n".join(self.reminders_list)) # Update the label
            add_reminder_window.destroy()

        ctk.CTkButton(add_reminder_window, text="Save", command=save_reminder).pack(pady=10)

    def remove_reminder(self):
        """Open a window to remove a reminder."""
        if not self.reminders_list:
            # If there are no reminders, show a message
            messagebox.showinfo("No Reminders", "There are no reminders to remove.")
            return

        remove_reminder_window = ctk.CTkToplevel(self)
        remove_reminder_window.title("Remove Reminder")
        remove_reminder_window.geometry("300x200")

        ctk.CTkLabel(remove_reminder_window, text="Select a Reminder to Remove:").pack(pady=5)

        # Dropdown menu to select a reminder
        selected_reminder = ctk.StringVar(remove_reminder_window)
        selected_reminder.set(self.reminders_list[0]) # Set the default value
        reminder_dropdown = ctk.CTkOptionMenu(
            remove_reminder_window,
            variable=selected_reminder,
            values=self.reminders_list,
        )
        reminder_dropdown.pack(pady=5)

        def confirm_removal():
            """Remove the selected reminder."""
            reminder_to_remove = selected_reminder.get()
            if reminder_to_remove in self.reminders_list:
                self.reminders_list.remove(reminder_to_remove) # Remove the reminder from the list
                self.reminder_present.configure(
                    text="\n".join(self.reminders_list) if self.reminders_list else "No reminders yet"
                ) # Update the label
            remove_reminder_window.destroy()

        ctk.CTkButton(
            remove_reminder_window,
            text="Remove",
            fg_color="red",
            hover_color="darkred",
            text_color="white",
            command=confirm_removal,
        ).pack(pady=10)

# Create the main Tkinter window
root = App()

# Run the Tkinter main loop
root.mainloop()