from functools import partial
from tkinter import *
from tkinter import Image as TkImage
from tkinter import ttk
from ttkthemes import ThemedTk
import ctypes as ct
from mathematics import calculate_expression, plot, solve, convert, scientific
from enum import Enum
from PIL import ImageTk, Image

Mode = Enum('Mode', 'Calculator Solve Scientific Plot Conversion')

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

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.frame = None
        self.create_menu()
        self.set_mode(Mode.Calculator)

    def create_menu(self):
        menu = Menu(self.master)
        menu.config(background='#323233', foreground='white')
        self.master.config(menu=menu)

        modeMenu = Menu(menu, background='#323233', foreground='white', tearoff=False)
        modeMenu.add_command(label='Calculator', command=partial(self.set_mode, Mode.Calculator))
        modeMenu.add_command(label='Solve for x', command=partial(self.set_mode, Mode.Solve))
        modeMenu.add_command(label='Scientific notation', command=partial(self.set_mode, Mode.Scientific))
        modeMenu.add_command(label='Plot', command=partial(self.set_mode, Mode.Plot))
        modeMenu.add_command(label='Unit conversion', command=partial(self.set_mode, Mode.Conversion))
        menu.add_cascade(label='Mode', menu=modeMenu)
    
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

    def create_calculator_widgets(self):
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
        self.frame.rowconfigure(2, weight=1)

        self.entry_field.bind('<Return>', self.evaluate)
        self.entry_field.focus()

    def create_plot_widgets(self):
        if self.master.winfo_width() < 650 or self.master.winfo_height() < 700:
            self.master.geometry('650x700')

        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, columnspan=2, sticky=E+W+N+S)

        img = ImageTk.PhotoImage(Image.open('assets/placeholder_plot.png'))
        self.plot_image = ttk.Label(self.frame, anchor='center')
        self.plot_image.configure(image=img)
        self.plot_image.image = img
        self.plot_image.grid(row=1, column=0, columnspan=2, sticky=E+W+N+S)

        min_x_label = ttk.Label(self.frame, text='Min x:', anchor='sw')
        min_x_label.grid(row=2, column=0, sticky=E+W+N+S)
        max_x_label = ttk.Label(self.frame, text='Max x:', anchor='s')
        max_x_label.grid(row=2, column=1, sticky=E+W+N+S)
        self.min_x_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.min_x_entry_field.grid(row=3, column=0, sticky=E+W+N+S)
        self.max_x_entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.max_x_entry_field.grid(row=3, column=1, sticky=E+W+N+S)

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
        self.entry_field.focus()

    def create_conversion_widgets(self):
        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0, sticky=E+W+N+S)

        self.result_field = ttk.Label(self.frame, text='\n', font=('Arial', 30), anchor='center')
        self.result_field.grid(row=0, column=0, columnspan=2, sticky=E+W+N+S)

        self.label = ttk.Label(self.frame, text='Enter the amount of the unit to convert:', anchor='sw')
        self.label.grid(row=1, column=0, columnspan=2, sticky=E+W+N+S)
        self.entry_field = ttk.Entry(self.frame, font=('Arial', 20))
        self.entry_field.grid(row=2, column=0, columnspan=2, sticky=E+W+N+S)

        unit_from_label = ttk.Label(self.frame, text='Unit from:', anchor='sw')
        unit_from_label.grid(row=3, column=0, sticky=E+W+N+S)
        unit_to_label = ttk.Label(self.frame, text='Unit to:', anchor='s')
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
                    img = ImageTk.PhotoImage(Image.open(file_path))
                    self.plot_image.configure(image=img)
                    self.plot_image.image = img
            case Mode.Conversion:
                self.result_field['text'] = f'\n{result}\n'

if __name__ == '__main__':
    root = ThemedTk(className='Math GUI', theme='equilux')
    # Set favicon
    img = TkImage("photo", file='assets/calculator_icon.png')
    root.iconphoto(True, img)

    root.geometry('800x300')

    # Dark mode
    root.config(background='#1e1e1e')
    dark_title_bar(root)
    
    app = Application(master=root)
    app.mainloop()