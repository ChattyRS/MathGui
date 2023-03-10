from functools import partial
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk
import ctypes as ct
from mathematics import calculate_expression, plot, solve, convert, scientific
from enum import Enum

Mode = Enum('Mode', 'Calculator Solve Plot Scientific Conversion')

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
        self.pack()
        self.set_mode(Mode.Calculator)
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menu = Menu(self.master)
        menu.config(background='#323233', foreground='white')
        self.master.config(menu=menu)

        modeMenu = Menu(menu, background='#323233', foreground='white', tearoff=False)
        modeMenu.add_command(label='Calculator', command=partial(self.set_mode, Mode.Calculator))
        modeMenu.add_command(label='Solve for x', command=partial(self.set_mode, Mode.Solve))
        modeMenu.add_command(label='Scientific notation', command=partial(self.set_mode, Mode.Scientific))
        # modeMenu.add_command(label='Unit conversion', command=partial(self.set_mode, Mode.Conversion))
        # modeMenu.add_command(label='Plot', command=partial(self.set_mode, Mode.Plot))
        menu.add_cascade(label='Mode', menu=modeMenu)
    
    def set_mode(self, mode: Mode):
        self.mode = mode
        self.master.title(f'Math GUI - {mode.name}')

    def create_widgets(self):
        self.result_field = ttk.Label(self, text='\n\n\n')
        self.result_field.pack(side='top', fill='x')

        self.label = ttk.Label(self, text='Enter your mathematical expression:')
        self.label.pack(side='top', fill='x')
        self.entry_field = ttk.Entry(self, width=50)
        self.entry_field.pack(side='bottom', fill='x')

        self.entry_field.bind('<Return>', self.evaluate)
        self.entry_field.focus()
    
    def evaluate(self, _):
        input = self.entry_field.get()

        result = ''
        match self.mode:
            case Mode.Calculator:
                result = calculate_expression(input)
            case Mode.Solve:
                result = solve(input)
            case Mode.Plot:
                result = plot(input)
            case Mode.Scientific:
                result = scientific(input)
            case Mode.Conversion:
                result = convert(input)

        self.result_field['text'] = f'Result:\n\n\t{result}\n'

if __name__ == '__main__':
    root = ThemedTk(className='Math GUI', theme='equilux')
    # Set favicon
    img = Image("photo", file='assets/calculator_icon.png')
    root.iconphoto(True, img)

    root.config(background='#1e1e1e')
    dark_title_bar(root)
    
    app = Application(master=root)
    app.mainloop()