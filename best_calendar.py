from tkinter import *
from tkcalendar import Calendar
from dataclasses import dataclass
from datetime import date
import customtkinter as ctk

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


class App(ctk.CTk):
    """
    The main application class for the calendar app.
    """

    def __init__(self):
        """
        Initialize the application.

        :ivar frame: The main frame of the application.
        :ivar calendar: The custom calendar widget.
        :ivar event_window: The window for adding events.
        :ivar title_entry: The entry widget for the event title.
        :ivar event_type: The variable for the event type dropdown.
        :ivar type_dropdown: The dropdown menu for selecting event types.
        """

        super().__init__()
        self.title("Best Calendar")
        self.geometry("700x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)

        # Create the calendar
        self.calendar = BestCalendar(self.frame, year=2025, month=3, day=22, font="Arial 14", locale='en_US', disabledforeground='red',
               cursor="hand2", background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
               selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])

        self.calendar.pack(fill="both", expand=True, pady=20)

        # Bind the click event to the calendar
        self.calendar.bind("<<CalendarSelected>>", self.on_date_click)

    def submit_event(self):
        """
        Submit a new event to the calendar.
        """
        title = self.title_entry.get()
        event_type_value = self.event_type.get()
        if title:  # Ensure the title is not empty
            new_event = Event(day, month, year, title, event_type_value)
            self.calendar.add_event(new_event)
            self.event_window.destroy()  # Close the event window

    def on_date_click(self, event):
        """
        Handle the event when a date is clicked in the calendar.

        :param event: The event object triggered by the click.
        """
        selected_date = self.calendar.get_selected_date()
        self.open_event_menu(selected_date)

    def open_event_menu(self, selected_date):
        """
        Open the event menu for adding a new event.

        :param selected_date: The selected date in MM/DD/YY format.
        """
        # Create a new CTkToplevel window
        self.event_window = ctk.CTkToplevel(self)
        self.event_window.title("Add Event")
        self.event_window.geometry("300x250")

        # Parse the selected date (MM/DD/YY format)
        month, day, year = map(int, selected_date.split('/'))
        year += 2000  # Convert 2-digit year to 4-digit year

        # Event title input
        ctk.CTkLabel(self.event_window, text="Event Title:").pack(pady=5)
        self.title_entry = ctk.CTkEntry(self.event_window)
        self.title_entry.pack(pady=5)

        # Event type dropdown
        ctk.CTkLabel(self.event_window, text="Event Type:").pack(pady=5)
        self.event_type = StringVar(self.event_window)
        self.event_type.set("Exam")  # Default value
        self.type_dropdown = ctk.CTkOptionMenu(self.event_window, variable=self.event_type, values=["Exam", "Homework", "Quiz"])
        self.type_dropdown.pack(pady=5)

        # Submit button
        ctk.CTkButton(self.event_window, text="Add Event", command=self.submit_event, fg_color="blue", hover_color="darkblue", text_color="white").pack(pady=30)


# Create the main Tkinter window
root = App()

# Run the Tkinter main loop
root.mainloop()