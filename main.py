from functools import partial
import inspect
from tkinter import *
from tkinter import Image as TkImage
from tkinter import ttk
from ttkthemes import ThemedTk
import ctypes as ct
from mathematics import calculate_expression, plot, solve, convert, scientific, get_units, get_random_primes
from enum import Enum
from PIL import ImageTk, Image
import webbrowser
import pyperclip

Mode = Enum('Mode', 'Calculator Solve Scientific Plot Conversion Primes')

def create_themed_window(root=False) -> ThemedTk:
    '''
    Creates a themed (equilux) window in dark mode.
    '''
    window = ThemedTk(className='Math GUI', theme='equilux') if root else Toplevel()
    # Set favicon
    img = TkImage('photo', file='assets/calculator_icon.png')
    window.iconphoto(True, img)

    # Dark mode
    window.config(background='#1e1e1e')
    dark_title_bar(window)

    return window

def dark_title_bar(window):
    '''
    https://stackoverflow.com/a/70724666
    '''
    if not hasattr(ct, 'windll'):
        return
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                         ct.sizeof(value))
    
class HelpWindow(Frame):
    def __init__(self, master: ThemedTk, help_text=''):
        super().__init__(master)
        self.master = master
        self.frame = None

        self.create_help_widgets(help_text)
    
    def create_help_widgets(self, help_text=''):
        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.help_label = ttk.Label(self.frame, text=help_text, anchor='w')
        self.help_label.grid(row=0, column=0, sticky=E+W+N+S)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

class Application(Frame):
    def __init__(self, master: ThemedTk):
        super().__init__(master)
        self.master = master
        self.frame = None
        self.create_menu()

        # Entry style to highlight selection
        ttk.Style().configure('TEntry', selectbackground='#002c5e')

        self.set_mode(Mode.Calculator)

    def create_menu(self):
        menu = Menu(self.master, background='#323233', foreground='#a6a6a6')
        self.master.config(menu=menu)

        modeMenu = Menu(menu, background='#464646', foreground='#a6a6a6', tearoff=False)
        modeMenu.add_command(label='Calculator', command=partial(self.set_mode, Mode.Calculator))
        modeMenu.add_command(label='Solve for x', command=partial(self.set_mode, Mode.Solve))
        modeMenu.add_command(label='Scientific notation', command=partial(self.set_mode, Mode.Scientific))
        modeMenu.add_command(label='Plot', command=partial(self.set_mode, Mode.Plot))
        modeMenu.add_command(label='Unit conversion', command=partial(self.set_mode, Mode.Conversion))
        modeMenu.add_command(label='Prime generator', command=partial(self.set_mode, Mode.Primes))
        menu.add_cascade(label='Mode', menu=modeMenu)

        helpMenu = Menu(menu, background='#464646', foreground='#a6a6a6', tearoff=False)
        helpMenu.add_command(label='Help', command=self.show_help)
        helpMenu.add_command(label='GitHub', command=self.open_github_page)
        helpMenu.add_command(label='Support (join Discord)', command=self.open_discord)
        menu.add_cascade(label='Help', menu=helpMenu)
    
    def set_mode(self, mode: Mode):
        self.mode = mode
        self.master.title(f'Math GUI - {mode.name}')
        if self.frame:
            self.frame.destroy()
        match self.mode:
            case Mode.Calculator:
                self.create_calculator_widgets()
            case Mode.Solve:
                self.create_calculator_widgets()
            case Mode.Scientific:
                self.create_calculator_widgets()
            case Mode.Plot:
                self.create_plot_widgets()
            case Mode.Conversion:
                self.create_conversion_widgets()
            case Mode.Primes:
                self.create_prime_widgets()
    
    def show_help(self):
        match self.mode:
            case Mode.Calculator:
                help_text = inspect.getdoc(calculate_expression)
            case Mode.Solve:
                help_text = inspect.getdoc(solve)
            case Mode.Scientific:
                help_text = inspect.getdoc(scientific)
            case Mode.Plot:
                help_text = inspect.getdoc(plot)
            case Mode.Conversion:
                help_text = inspect.getdoc(convert)
                help_text += f'\n\nSupported units:\n{get_units()}'
            case Mode.Primes:
                help_text = inspect.getdoc(get_random_prime)
        help_root = create_themed_window()
        HelpWindow(help_root, help_text)

    def open_github_page(self):
        webbrowser.open('https://github.com/ChattyRS/MathGui')

    def open_discord(self):
        webbrowser.open('https://discord.gg/Pcbz2HH')

    def create_calculator_widgets(self):
        if self.master.winfo_width() < 1000 or self.master.winfo_height() < 400:
            self.master.geometry('1000x400')
            
        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n\n\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, sticky=E+W+N+S)

        match self.mode:
            case Mode.Calculator:
                self.label = ttk.Label(self.frame, text='Enter an expression:', anchor='sw')
            case Mode.Solve:
                self.label = ttk.Label(self.frame, text='Enter an equality for x:', anchor='sw')
            case Mode.Scientific:
                self.label = ttk.Label(self.frame, text='Enter a value in normal or scientific notation:', anchor='sw')
        
        self.label.grid(row=1, column=0, sticky=E+W+N+S)
        self.entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.entry_field.grid(row=2, column=0, sticky=E+W+N+S)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.entry_field.bind('<Return>', self.evaluate)
        self.entry_field.focus()

    def create_plot_widgets(self):
        if self.master.winfo_width() < 650 or self.master.winfo_height() < 700:
            self.master.geometry('650x700')

        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, columnspan=2, sticky=E+W+N+S)

        self.plot_original = Image.open('assets/placeholder_plot.png')
        self.plot_resized = ImageTk.PhotoImage(self.plot_original)
        self.plot_image = Canvas(self.frame, border=0, highlightthickness=0)
        self.plot_image.create_image(0, 0, image=self.plot_resized, anchor='nw', tags='IMG')
        self.plot_image.grid(row=0, sticky=W+E+N+S)
        self.plot_image.grid(row=1, column=0, columnspan=2, sticky=E+W+N+S)

        min_x_label = ttk.Label(self.frame, text='Min x:', anchor='sw')
        min_x_label.grid(row=2, column=0, sticky=E+W+N+S)
        max_x_label = ttk.Label(self.frame, text='Max x:', anchor='sw')
        max_x_label.grid(row=2, column=1, sticky=E+W+N+S)
        self.min_x_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.min_x_entry_field.grid(row=3, column=0, sticky=E+W+N+S)
        self.min_x_entry_field.insert(0, '-10')
        self.max_x_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.max_x_entry_field.grid(row=3, column=1, sticky=E+W+N+S)
        self.max_x_entry_field.insert(0, '10')

        self.label = ttk.Label(self.frame, text='Enter a function of x:', anchor='sw')
        self.label.grid(row=4, column=0, columnspan=2, sticky=E+W+N+S)
        self.entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.entry_field.grid(row=5, column=0, columnspan=2, sticky=E+W+N+S)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.entry_field.bind('<Return>', self.evaluate)
        self.min_x_entry_field.bind('<Return>', self.evaluate)
        self.max_x_entry_field.bind('<Return>', self.evaluate)
        self.plot_image.bind("<Configure>", self.resize)
        self.entry_field.focus()

    def resize(self, event):
        size = (event.width, event.height)
        resized = self.plot_original.resize(size, Image.LANCZOS)
        self.plot_resized = ImageTk.PhotoImage(resized)
        self.plot_image.delete("IMG")
        self.plot_image.create_image(0, 0, image=self.plot_resized, anchor='nw', tags='IMG')

    def create_conversion_widgets(self):
        if self.master.winfo_width() < 1000 or self.master.winfo_height() < 400:
            self.master.geometry('1000x400')

        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, columnspan=2, sticky=E+W+N+S)

        self.label = ttk.Label(self.frame, text='Enter the amount of the unit to convert:', anchor='sw')
        self.label.grid(row=1, column=0, columnspan=2, sticky=E+W+N+S)
        self.entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.entry_field.insert(0, '1')
        self.entry_field.grid(row=2, column=0, columnspan=2, sticky=E+W+N+S)

        unit_from_label = ttk.Label(self.frame, text='Unit from:', anchor='sw')
        unit_from_label.grid(row=3, column=0, sticky=E+W+N+S)
        unit_to_label = ttk.Label(self.frame, text='Unit to:', anchor='sw')
        unit_to_label.grid(row=3, column=1, sticky=E+W+N+S)
        self.unit_from_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.unit_from_entry_field.grid(row=4, column=0, sticky=E+W+N+S)
        self.unit_to_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.unit_to_entry_field.grid(row=4, column=1, sticky=E+W+N+S)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.entry_field.bind('<Return>', self.evaluate)
        self.unit_from_entry_field.bind('<Return>', self.evaluate)
        self.unit_to_entry_field.bind('<Return>', self.evaluate)
        self.entry_field.focus()

    def create_prime_widgets(self):
        if self.master.winfo_width() < 1000 or self.master.winfo_height() < 400:
            self.master.geometry('1000x400')

        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n\n\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=E+W+N+S)

        self.copy_button = ttk.Button(self.frame, text='Copy', command=self.to_clipboard)
        self.copy_button.grid(row=1, column=1, sticky=E+W+N+S)

        self.label = ttk.Label(self.frame, text='Number of digits:', anchor='sw')
        self.label.grid(row=2, column=0, columnspan=2, sticky=E+W+N+S)

        self.entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.entry_field.grid(row=3, column=0, columnspan=2, sticky=E+W+N+S)

        self.file_types = ['.txt', '.csv']
        self.var_file_type = StringVar(value=self.file_types[0])
        for i, v in enumerate(self.file_types):
            file_type_field = ttk.Radiobutton(self.frame, text=v, value=v, variable=self.var_file_type)
            file_type_field.grid(row=4+i, column=1, sticky=E+W+N+S)

        self.number_of_primes_label = ttk.Label(self.frame, text='Number primes to generate (output will be written to file in output folder when > 1):', anchor='sw')
        self.number_of_primes_label.grid(row=4, column=0, sticky=E+W+N+S)

        self.number_of_primes_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.number_of_primes_field.grid(row=5, column=0, sticky=E+W+N+S)
        self.number_of_primes_field.insert(0, '1')

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.entry_field.bind('<Return>', self.evaluate)
        self.number_of_primes_field.bind('<Return>', self.evaluate)
        self.entry_field.focus()
    
    def to_clipboard(self):
        to_copy = self.result_field['text'].strip()
        pyperclip.copy(to_copy)
    
    def evaluate(self, _):
        input = self.entry_field.get()

        result, file_path = '', None
        try:
            match self.mode:
                case Mode.Calculator:
                    result = calculate_expression(input) + '\n'
                case Mode.Solve:
                    result = solve(input) + '\n'
                case Mode.Scientific:
                    result = scientific(input) + '\n'
                case Mode.Plot:
                    min_x = self.min_x_entry_field.get()
                    max_x = self.max_x_entry_field.get()
                    result, file_path = plot(min_x, max_x, input)
                case Mode.Conversion:
                    unit_from = self.unit_from_entry_field.get()
                    unit_to = self.unit_to_entry_field.get()
                    result = convert(input, unit_from, unit_to)
                case Mode.Primes:
                    num_of_primes = self.number_of_primes_field.get()
                    file_type = self.var_file_type.get()
                    result = get_random_primes(num_of_primes, file_type, input)
        except Exception as e:
            result = str(e)
            print(result)
        
        match self.mode:
            case Mode.Calculator:
                self.result_field['text'] = f'\n{result}\n'
            case Mode.Solve:
                self.result_field['text'] = f'\n{result}\n'
            case Mode.Scientific:
                self.result_field['text'] = f'\n{result}\n'
            case Mode.Plot:
                self.result_field['text'] = f'\n{result}' if not '\n' in result else result
                if file_path:
                    self.plot_original = Image.open(file_path)
                    size = (self.plot_resized.width(), self.plot_resized.height())
                    resized = self.plot_original.resize(size, Image.LANCZOS)
                    self.plot_resized = ImageTk.PhotoImage(resized)
                    self.plot_image.delete("IMG")
                    self.plot_image.create_image(0, 0, image=self.plot_resized, anchor='nw', tags='IMG')
            case Mode.Conversion:
                self.result_field['text'] = f'\n{result}\n'
            case Mode.Primes:
                self.result_field['text'] = f'\n{result}\n'

if __name__ == '__main__':
    root = create_themed_window(True)
    root.geometry('1000x400')
    
    app = Application(master=root)
    app.mainloop()