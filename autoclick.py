#import Library
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import pyautogui
from tkinter import ttk
import threading
import time
import json
import webbrowser
import keyboard


#Add option dialog
class OptionSelectionDialog:
    def __init__(self, parent):
        self.parent = parent

        self.text_dialog_edit = None

        self.key_listening = False
        
        self.key_listening_index = None

        self.result = None

        self.auto_thread = None

        self.scroll_amount = 0

        self.options = [
            "Click on Image",
            "Move Mouse Pointer",
            "Click Left Mouse At",
            "Click Right Mouse At",
            "Auto Press Key",
            "Auto Enter Text",
            "Time Delay",
            "Hold Key",
            "Release Key",
            "Click Left Mouse",
            "Click Right Mouse",
            "Hold Mouse",
            "Release Mouse",
            "Scroll"
        ]

        self.option_var = tk.StringVar(value=self.options[0])

        option_combobox = ttk.Combobox(parent, textvariable=self.option_var, values=self.options, state="readonly")
        option_combobox.pack(padx=20, pady=10)

        button_frame = tk.Frame(parent)
        button_frame.pack()

        ok_button = ttk.Button(button_frame, text="OK", width=13, command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", width=13, command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    def on_ok(self):
        self.result = self.option_var.get()
        self.parent.destroy()

    def on_cancel(self):
        self.parent.destroy()



class AutoClickerApp:
    def __init__(self, root):
        keyboard.add_hotkey('F12', self.toggle_auto_with_shortcut)

        self.hold_key_listening = False

        self.auto_press_key_listening = False

        self.release_key_listening = False

        self.key_mapping = {
            "Control_L": "ctrl",
            "Control_R": "ctrl",
            "Alt_L": "alt",
            "Alt_R": "alt",
            "Shift_L": "shift",
            "Shift_R": "shift"
        }

        self.auto_running = False

        self.root = root

        self.root.title("AutoOpExe")

        self.root.geometry("600x300")

        self.pressed_keys = []

        self.style = ttk.Style(root)

        self.style.theme_use('vista')

        KEY_MAPPING = {
            "Control_L": "ctrl",
            "Control_R": "ctrl",
            "Alt_L": "alt",
            "Alt_R": "alt",
            "Shift_L": "shift",
            "Shift_R": "shift"
        }

        self.options = []

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.option_listbox = tk.Listbox(main_frame, selectmode=tk.SINGLE, width=40)
        self.option_listbox.pack(pady=5, padx=10, side=tk.TOP, fill=tk.BOTH, expand=True)

        self.selected_index = None

        self.option_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
        self.option_listbox.bind("<ButtonRelease-1>", self.on_listbox_drag_release)

        self.repeat_var = tk.StringVar(value="Off")
        self.repeat_radio_frame = ttk.Frame(main_frame)
        self.repeat_radio_frame.pack(pady=5, padx=10, side=tk.LEFT)

        self.repeat_radio_label = ttk.Label(self.repeat_radio_frame, text="Repeat Time:")
        self.repeat_radio_label.pack(side=tk.LEFT)

        self.repeat_radio_on = ttk.Radiobutton(self.repeat_radio_frame, text="On", variable=self.repeat_var, value="On")
        self.repeat_radio_on.pack(side=tk.LEFT)

        self.repeat_radio_infinite = ttk.Radiobutton(self.repeat_radio_frame, text="Infinite", variable=self.repeat_var, value="Infinite")
        self.repeat_radio_infinite.pack(side=tk.LEFT)

        self.repeat_radio_off = ttk.Radiobutton(self.repeat_radio_frame, text="Off", variable=self.repeat_var, value="Off")
        self.repeat_radio_off.pack(side=tk.LEFT)

        self.repeat_input_frame = ttk.Frame(main_frame)
        self.repeat_input_frame.pack(pady=5, padx=10, side=tk.LEFT)

        self.repeat_label = ttk.Label(self.repeat_input_frame, text="Repeat Count:")
        self.repeat_label.pack(side=tk.LEFT)

        self.repeat_entry = ttk.Entry(self.repeat_input_frame, width=5)
        self.repeat_entry.pack(side=tk.LEFT)

        self.add_button = ttk.Button(main_frame, text="Add Option", command=self.show_option_dialog)
        self.add_button.pack(pady=5, padx=10, side=tk.LEFT)

        self.start_button = ttk.Button(main_frame, text="Start", command=self.toggle_auto)
        self.start_button.pack(pady=5, padx=10, side=tk.LEFT)

        self.ctrl_pressed = False

        self.auto_click_position_enabled = False

        self.auto_click_left_position_enabled = False

        self.auto_click_right_position_enabled = False
        

        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.option_listbox.bind("<Button-3>", self.show_context_menu)


        self.repeat_var.trace("w", self.on_repeat_change)
        self.repeat_entry.config(state=tk.DISABLED)

        menubar = tk.Menu(root)

        root.config(menu=menubar)

        #file menu
        file_menu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Options", command=self.save_options)
        file_menu.add_command(label="Import Options", command=self.load_options)

        self.root.resizable(False, False)

        #edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Edit Option", command=self.edit_option)
        edit_menu.add_command(label="Add Option", command=self.show_option_dialog)

        edit_menu.add_command(label="Clear All Options", command=self.clear_all_options)

        #help menu
        

    def open_help(self):
        webbrowser.open('index.html')
    

    def open_report_idea(self):
        webbrowser.open('report_idea.html')


    def toggle_auto_with_shortcut(self):
        self.toggle_auto()


    def edit_option(self):
        selected_index = self.option_listbox.curselection()
        
        if not selected_index:
            messagebox.showerror("Error", "Please select an option first.")
            return

        index = selected_index[0]

        action, option = self.options[index]
       
        if selected_index:
            index = selected_index[0]
            action, option = self.options[index]

            if action == "Click on Image":
                file_path = filedialog.askopenfilename(title="Select an image file", filetypes=[("Image files", "*.png"), ("All files", "*.*")])

                if file_path:
                    self.options[index] = ("Click on Image", file_path)
                    self.update_option_listbox()

            elif action == "Auto Enter Text":
                self.show_auto_enter_text_dialog_edit()

            elif action == "Time Delay":
                wait_time = self.ask_integer("Edit Time Delay", "Enter the new Time Delay in seconds:", default_value=int(option))

                if wait_time is not None:
                    self.options[index] = ("Time Delay", wait_time)
                    self.update_option_listbox()

            elif action == "Move Mouse Pointer":
                messagebox.showinfo("Edit Move Mouse Pointer", "Press Ctrl + Q to capture the new Move Mouse Pointer position.")
                self.auto_click_position_enabled = True
                self.options[index] = ("Move Mouse Pointer", "<waiting>")
                self.update_option_listbox()

            elif action == "Click Left Mouse At":
                messagebox.showinfo("Edit Click Position Mouse", "Press Ctrl + Q to capture the new Click Left Mouse position.")
                self.auto_click_left_position_enabled = True
                self.options[index] = ("Click Left Mouse At", "<waiting>")
                self.update_option_listbox()

            elif action == "Click Right Mouse At":
                messagebox.showinfo("Edit Click Position Mouse", "Press Ctrl + Q to capture the new Click Right Mouse position.")
                self.auto_click_right_position_enabled = True
                self.options[index] = ("Click Right Mouse At", "<waiting>")
                self.update_option_listbox()

            elif action == "Auto Press Key":
                messagebox.showinfo("Edit Auto Press Key", "Press the new key combination.")
                self.options[index] = ("Auto Press Key", "<listening>")
                self.update_option_listbox()

            elif action == "Scroll":
                self.scroll_amount = self.ask_integer("Scroll Amount", "Enter the new scroll amount (+/-):")
                self.options[index] = ("Scroll", self.scroll_amount)
                self.update_option_listbox()

            elif action == "Hold Key":                
                self.options[index] = ("Hold Key", "<listening>")
                self.hold_key_listening_index = True
                self.update_option_listbox()

            elif action == "Release Key":                
                self.options[index] = ("Release Key", "<listening>")
                self.release_key_listening_index = True
                self.update_option_listbox()

            elif action == "Hold Left Mouse":
                self.create_new_window_hold_edit(index)

            elif action == "Hold Right Mouse":
                self.create_new_window_hold_edit(index)

            elif action == "Release Left Mouse":
                self.create_new_window_release_edit(index)

            elif action == "Release Right Mouse":
                self.create_new_window_release_edit(index)


    def clear_all_options(self):
        self.options = []
        self.update_option_listbox()


    def on_listbox_select(self, event):
        self.selected_index = self.option_listbox.curselection()


    def on_listbox_drag_release(self, event):
        if self.selected_index is not None:
            new_index = self.option_listbox.nearest(event.y)

            if new_index != self.selected_index[0]:
                # Move the selected item to the new position
                option = self.options.pop(self.selected_index[0])
                self.options.insert(new_index, option)
                self.update_option_listbox()


    def save_options(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])

        if file_path:
            options_to_save = [{"action": action, "option": option} for action, option in self.options]
            with open(file_path, "w") as f:
                json.dump(options_to_save, f, indent=4)
            messagebox.showinfo("Save Options", "Options have been saved successfully.")


    def load_options(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])

        if file_path:
            try:
                with open(file_path, "r") as f:
                    loaded_options = json.load(f)

                self.options = [(option["action"], option["option"]) for option in loaded_options]
                self.update_option_listbox()
                messagebox.showinfo("Load Options", "Options have been loaded successfully.")

            except Exception as e:
                messagebox.showerror("Error", "Failed to load options from the selected file.")


    def on_repeat_change(self, *args):
        if self.repeat_var.get() == "Infinite":
            self.repeat_entry.config(state=tk.DISABLED)

        elif self.repeat_var.get() == "Off":
            self.repeat_entry.config(state=tk.DISABLED)

        else:
            self.repeat_entry.config(state=tk.NORMAL)


    def start_auto(self):
        repeat_mode = self.repeat_var.get()
        repeat_count = 1

        if repeat_mode == "On":
            try:
                repeat_count = int(self.repeat_entry.get())
                if repeat_count <= 0:
                    raise ValueError()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid repeat count. Please enter a positive integer.")
                self.auto_running = False
                self.start_button.config(text="Start")
                return
            
        for _ in range(repeat_count):
            if not self.auto_running:
                break
            
            for action, option in self.options:
                if action == "Time Delay":
                    wait_time = option
                    time.sleep(wait_time)

                else:
                    self.execute_option(action, option)

        self.auto_running = False
        self.start_button.config(text="Start")


    def toggle_auto(self):
        if not self.auto_running:
            if self.repeat_var.get() == "Infinite":
                self.auto_thread = threading.Thread(target=self.start_auto_infinite)

            else:
                self.auto_thread = threading.Thread(target=self.start_auto)

            self.auto_thread.start()
            self.auto_running = True
            self.start_button.config(text="Stop")

        else:
            self.auto_running = False
            self.start_button.config(text="Start")
            
            if self.auto_thread:
                self.auto_thread.join()


    def start_auto_infinite(self):
        if self.auto_running:
            for action, option in self.options:

                if not self.auto_running:
                    break

                if action == "Time Delay":
                    wait_time = option
                    time.sleep(wait_time)

                else:
                    self.execute_option(action, option)

            self.start_auto_infinite()


    def show_option_dialog(self):
        option_dialog = tk.Toplevel(self.root)
        option_dialog.title("Select an option")

        app_x = self.root.winfo_x()
        app_y = self.root.winfo_y()
        app_width = self.root.winfo_width()
        app_height = self.root.winfo_height()

        option_width = 250
        option_height = 130

        option_x = app_x + (app_width - option_width) // 2
        option_y = app_y + (app_height - option_height) // 2

        option_dialog.geometry(f"+{option_x}+{option_y}")

        option_selection = OptionSelectionDialog(option_dialog)

        option_dialog.resizable(False, False)

        option_dialog.wait_window()
        option_type = option_selection.result

        if option_type:
            if option_type == "Click on Image":
                file_path = filedialog.askopenfilename(title="Select an image file", filetypes=[("Image files", "*.png"), ("All files", '*')])
                
                if file_path:
                    self.add_option("Click on Image", file_path)

            elif option_type == "Auto Press Key":
                self.add_option("Auto Press Key", "<listening>")

            elif option_type == "Auto Enter Text":
                self.show_auto_enter_text_dialog()

            elif option_type == "Time Delay":
                wait_time = self.ask_integer("Time Delay", "Enter the Time Delay in seconds:")

                if wait_time is not None:
                    self.add_option("Time Delay", wait_time)
                    
            elif option_type == "Move Mouse Pointer":
                self.add_option("Move Mouse Pointer", "<waiting>")
                self.auto_click_position_enabled = True
                messagebox.showinfo("Move Mouse Pointer", "Press Ctrl + Q to capture the Move Mouse Pointer position.")
            
            elif option_type == "Click Left Mouse At":
                self.add_option("Click Left Mouse At", "<waiting>")
                self.auto_click_left_position_enabled = True
                messagebox.showinfo("Click Left Mouse At", "Press Ctrl + Q to capture the Click Left Mouse position.")
            
            elif option_type == "Click Right Mouse At":
                self.add_option("Click Right Mouse At", "<waiting>")
                self.auto_click_right_position_enabled = True
                messagebox.showinfo("Click Right Mouse At", "Press Ctrl + Q to capture the Click Right Mouse position.")
            
            elif option_type == "Hold Left Mouse":
                self.add_option("Hold Left Mouse", "")

            elif option_type == "Release Left Mouse":
                self.add_option("Release Left Mouse", "")

            elif option_type == "Hold Right Mouse":
                self.add_option("Hold Right Mouse", "")

            elif option_type == "Release Right Mouse":
                self.add_option("Release Right Mouse", "")

            elif option_type == "Click Left Mouse":
                self.add_option("Click Left Mouse", "")

            elif option_type == "Click Right Mouse":
                self.add_option("Click Right Mouse", "")

            elif option_type == "Scroll":
                scroll_amount = self.ask_integer("Scroll Amount", "Enter the scroll amount (+/-):")

                if scroll_amount is not None:
                    self.add_option("Scroll", scroll_amount)

            elif option_type == "Hold Key":
                self.add_option("Hold Key", "<listening>")

            elif option_type == "Release Key":
                self.add_option("Release Key", "<listening>")

            elif option_type == "Hold Mouse":
                self.create_new_window_hold()

            elif option_type == "Release Mouse":
                self.create_new_window_release()


    def on_key_press(self, event):
        if any(opt[0] == "Hold Key" and opt[1] == "<listening>" for opt in self.options):
            self.hold_key_listening = True
            pressed_key = event.keysym
            pressed_key = self.key_mapping.get(pressed_key, pressed_key)

            if pressed_key not in self.pressed_keys:
                self.pressed_keys.append(pressed_key)


        if any(opt[0] == "Auto Press Key" and opt[1] == "<listening>" for opt in self.options):
            self.auto_press_key_listening = True
            pressed_key = event.keysym
            pressed_key = self.key_mapping.get(pressed_key, pressed_key)

            if pressed_key not in self.pressed_keys:
                self.pressed_keys.append(pressed_key)


        if any(opt[0] == "Release Key" and opt[1] == "<listening>" for opt in self.options):
            self.release_key_listening = True
            pressed_key = event.keysym
            pressed_key = self.key_mapping.get(pressed_key, pressed_key)

            if pressed_key not in self.pressed_keys:
                self.pressed_keys.append(pressed_key)


    def on_key_release(self, event):

        if self.hold_key_listening or self.auto_press_key_listening or self.release_key_listening:
            pressed_key = event.keysym
            pressed_key = self.key_mapping.get(pressed_key, pressed_key)

            if pressed_key in self.pressed_keys:
                key_combination = "+".join(self.pressed_keys)

                if self.hold_key_listening:
                    self.hold_key_listening = False
                    self.hold_key_listening_index = next((i for i, opt in enumerate(self.options) if opt[0] == "Hold Key" and opt[1] == "<listening>"), None)
                    
                    if self.hold_key_listening_index is not None:
                        self.options[self.hold_key_listening_index] = ("Hold Key", key_combination)
                        self.update_option_listbox()

                elif self.auto_press_key_listening:

                    self.auto_press_key_listening = False
                    self.auto_press_key_listening_index = next((i for i, opt in enumerate(self.options) if opt[0] == "Auto Press Key" and opt[1] == "<listening>"), None)
                    
                    if self.auto_press_key_listening_index is not None:
                        self.options[self.auto_press_key_listening_index] = ("Auto Press Key", key_combination)
                        self.update_option_listbox()

                elif self.release_key_listening:
                    self.release_key_listening = False
                    self.release_key_listening_index = next((i for i, opt in enumerate(self.options) if opt[0] == "Release Key" and opt[1] == "<listening>"), None)
                    
                    if self.release_key_listening_index is not None:
                        self.options[self.release_key_listening_index] = ("Release Key", key_combination)
                        self.update_option_listbox()

            self.pressed_keys = []


    def on_auto_move_position(self, event):
        
        if self.auto_click_position_enabled:
            x, y = pyautogui.position()
            self.options = [(action, f"{x}, {y}") if action == "Move Mouse Pointer" and option == "<waiting>" else (action, option) for action, option in self.options]
            self.update_option_listbox()
            self.auto_click_position_enabled = False

        elif self.auto_click_left_position_enabled:
            x, y = pyautogui.position()
            self.options = [(action, f"{x}, {y}") if action == "Click Left Mouse At" and option == "<waiting>" else (action, option) for action, option in self.options]
            self.update_option_listbox()
            self.auto_click_left_position_enabled = False

        elif self.auto_click_right_position_enabled:
            x, y = pyautogui.position()
            self.options = [(action, f"{x}, {y}") if action == "Click Right Mouse At" and option == "<waiting>" else (action, option) for action, option in self.options]
            self.update_option_listbox()
            self.auto_click_right_position_enabled = False


    def ask_string(self, title, prompt):
        return simpledialog.askstring(title, prompt)


    def ask_integer(self, title, prompt, default_value=None):
        value = simpledialog.askinteger(title, prompt, initialvalue=default_value)
        return value


    def add_option(self, action, option):
        self.options.append((action, option))
        self.update_option_listbox()


    def execute_option(self, action, option):
        if action == "Click on Image":
            image_location = pyautogui.locateOnScreen(option)


            if image_location:
                pyautogui.click(image_location)
                
        elif action == "Auto Press Key":
            keys = option.split("+")
            pyautogui.hotkey(*keys)

        elif action == "Auto Enter Text":
            pyautogui.write(option, interval=0.1)

        elif action == "Move Mouse Pointer":
            x, y = map(int, option.split(","))
            pyautogui.moveTo(x, y)

        elif action == "Hold Left Mouse":
            pyautogui.mouseDown()

        elif action == "Release Left Mouse":
            pyautogui.mouseUp()

        elif action == "Hold Right Mouse":
            pyautogui.mouseDown(button='right')

        elif action == "Release Right Mouse":
            pyautogui.mouseUp(button='right')

        elif action == "Click Left Mouse":
            pyautogui.click(button='left')

        elif action == "Click Right Mouse":
            pyautogui.click(button='right')

        elif action == "Scroll":
            pyautogui.scroll(option)

        elif action == "Hold Key":
            pyautogui.keyDown(option)

        elif action == "Release Key":
            pyautogui.keyUp(option)

        elif action == "Click Left Mouse At":
            x, y = map(int, option.split(","))
            pyautogui.click(x, y)

        elif action == "Click Right Mouse At":
            x, y = map(int, option.split(","))
            pyautogui.click(x, y, button='right')


    def start_auto(self):
        repeat_mode = self.repeat_var.get()
        repeat_count = 1

        if repeat_mode == "On":
            try:
                repeat_count = int(self.repeat_entry.get())

                if repeat_count <= 0:
                    raise ValueError()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid repeat count. Please enter a positive integer.")
                self.auto_running = False
                self.start_button.config(text="Start")
                return


        for _ in range(repeat_count):
            if not self.auto_running:
                break

            for action, option in self.options:

                if action == "Time Delay":
                    wait_time = option
                    time.sleep(wait_time)

                else:
                    self.execute_option(action, option)

        self.auto_running = False
        self.start_button.config(text="Start")
   

    def delete_option(self, index):
        self.option_listbox.delete(index)
        del self.options[index]


    def show_context_menu(self, event):
        selected_index = self.option_listbox.curselection()

        if selected_index:
            index = selected_index[0]
            context_menu = tk.Menu(self.option_listbox, tearoff=0)
            context_menu.add_command(label="Edit Option", command=self.edit_option)
            context_menu.add_command(label="Delete Option", command=lambda: self.delete_option(index))
            context_menu.post(event.x_root, event.y_root)

        else:
            context_menu = tk.Menu(self.option_listbox, tearoff=0)
            context_menu.add_command(label="Clear all option", command=self.clear_all_options)
            context_menu.add_command(label="Add option", command=self.show_option_dialog)
            context_menu.post(event.x_root, event.y_root)


    def update_option_listbox(self):
        self.option_listbox.delete(0, tk.END)

        for action, option in self.options:
            self.option_listbox.insert(tk.END, f"{action}: {option}")


    def show_auto_enter_text_dialog(self):
        text_dialog = tk.Toplevel(self.root)
        text_dialog.title("Enter Text")
        text_dialog.resizable(False, False)

        text_label = ttk.Label(text_dialog, text="Enter the text to type:")
        text_label.pack(pady=5, padx=10)
        
        text_area = tk.Text(text_dialog, height=7, width=40)
        text_area.pack(pady=5, padx=10)
        
        ok_button = ttk.Button(text_dialog, text="OK", command=lambda: self.add_auto_enter_text_option(text_area))
        ok_button.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        cancel_button = ttk.Button(text_dialog, text="Cancel", command=text_dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        open_file_button = ttk.Button(text_dialog, text="Open File", command=lambda: self.open_file_and_insert_into_text_area(text_area))
        open_file_button.pack(side=tk.LEFT, padx=(70, 0), pady=5)


    def open_file_and_insert_into_text_area(self, text_area):
        file_path = filedialog.askopenfilename(title="Open a text file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if file_path:
            try:
                with open(file_path, "r") as file:
                    file_content = file.read()
                    text_area.insert(tk.END, file_content)

            except Exception as e:
                messagebox.showerror("Error", "Failed to open and read the file.")


    def add_auto_enter_text_option(self, text_area):
        text = text_area.get("1.0", "end-1c")

        if text:
            self.add_option("Auto Enter Text", text)

        text_area.delete("1.0", tk.END)  # Xóa văn bản trong text area
        text_area.master.destroy()
        

    def show_auto_enter_text_dialog_edit(self):
        selected_index = self.option_listbox.curselection()
        
        if not selected_index:
            messagebox.showerror("Error", "Please select an option first.")
            return

        index = selected_index[0]
        action, option = self.options[index]

        if action != "Auto Enter Text":
            messagebox.showerror("Error", "You can only edit 'Auto Enter Text' options.")
            return

        self.text_dialog_edit = tk.Toplevel(self.root)
        self.text_dialog_edit.title("Edit Auto Enter Text")
        self.text_dialog_edit.resizable(False, False)

        text_label = ttk.Label(self.text_dialog_edit, text="Edit the text:")
        text_label.pack(pady=5, padx=10)

        edited_text_area = tk.Text(self.text_dialog_edit, height=7, width=40)
        edited_text_area.insert(tk.END, option)
        edited_text_area.pack(pady=5, padx=10)

        ok_button = ttk.Button(self.text_dialog_edit, text="OK", command=lambda: self.edit_auto_enter_text_option(index, edited_text_area.get("1.0", "end-1c")))
        ok_button.pack(side=tk.LEFT, padx=(10, 5), pady=5)

        cancel_button = ttk.Button(self.text_dialog_edit, text="Cancel", command=self.text_dialog_edit.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)


    def edit_auto_enter_text_option(self, index, edited_text):
        if edited_text:
            self.options[index] = ("Auto Enter Text", edited_text)
            self.update_option_listbox()

        self.text_dialog_edit.destroy()


    def on_closing(self):
        self.auto_running = False
        self.root.destroy()


    def create_new_window_hold(self):
        new_window = tk.Toplevel(root)
        new_window.title("Choose Mouse Action")
        new_window.geometry("270x80")
        new_window.resizable(False, False)

        frame = ttk.Frame(new_window)
        frame.grid(row=0, column=0, padx=10, pady=10)
    
        action_var = tk.StringVar()

        action_dropdown = ttk.Combobox(frame, textvariable=action_var, values=["Hold Mouse", "Release Mouse"], state="readonly", width=18)
        action_dropdown.grid(row=0, column=0, padx=0, pady=5)
        action_dropdown.set("Hold Mouse")

        label = ttk.Label(frame, text="Button")
        label.grid(row=0, column=1, padx=0, pady=5)

        button_var = tk.StringVar()

        button_dropdown = ttk.Combobox(frame, textvariable=button_var, values=["Left", "Right"], state="readonly", width=5)
        button_dropdown.grid(row=0, column=2, padx=10, pady=5)
        button_dropdown.set("Left")

        def get_action():
            action = action_var.get()

            button = button_var.get()

            result = f"{action.split()[0]} {button} Mouse"

            self.add_option(result, '')
            new_window.destroy()

        ok_button = ttk.Button(frame, text="OK", command=get_action, width=18)
        ok_button.grid(row=1, column=0, padx=(0,20), pady=5)

        cancel_button = ttk.Button(frame, text="Cancel", command=new_window.destroy, width=18)
        cancel_button.place(y=36, x=125)


    def create_new_window_hold_edit(self, index):
        new_window = tk.Toplevel(root)
        new_window.resizable(False, False)
        new_window.title("Choose Mouse Action")
        new_window.geometry("270x80")

        frame = ttk.Frame(new_window)
        frame.grid(row=0, column=0, padx=10, pady=10)

        action_var = tk.StringVar()

        action_dropdown = ttk.Combobox(frame, textvariable=action_var, values=["Hold Mouse", "Release Mouse"], state="readonly", width=18)
        action_dropdown.grid(row=0, column=0, padx=0, pady=5)
        action_dropdown.set("Hold Mouse")

        label = ttk.Label(frame, text="Button")
        label.grid(row=0, column=1, padx=0, pady=5)

        button_var = tk.StringVar()

        button_dropdown = ttk.Combobox(frame, textvariable=button_var, values=["Left", "Right"], state="readonly", width=5)
        button_dropdown.grid(row=0, column=2, padx=10, pady=5)
        button_dropdown.set("Left")

        def get_action():
            action = action_var.get()

            button = button_var.get()

            result = f"{action.split()[0]} {button} Mouse"

            self.options[index] = (result, '')
            self.update_option_listbox()

            new_window.destroy()

        ok_button = ttk.Button(frame, text="OK", command=get_action, width=18)
        ok_button.grid(row=1, column=0, padx=(0,20), pady=5)

        cancel_button = ttk.Button(frame, text="Cancel", command=new_window.destroy, width=18)
        cancel_button.place(y=36, x=125)

    
    def create_new_window_release(self):
        new_window = tk.Toplevel(root)
        new_window.resizable(False, False)
        new_window.title("Choose Mouse Action")
        new_window.geometry("270x80")

        frame = ttk.Frame(new_window)
        frame.grid(row=0, column=0, padx=10, pady=10)
    
        action_var = tk.StringVar()

        action_dropdown = ttk.Combobox(frame, textvariable=action_var, values=["Hold Mouse", "Release Mouse"], state="readonly", width=18)
        action_dropdown.grid(row=0, column=0, padx=0, pady=5)
        action_dropdown.set("Release Mouse")

        label = ttk.Label(frame, text="Button")
        label.grid(row=0, column=1, padx=0, pady=5)

        button_var = tk.StringVar()

        button_dropdown = ttk.Combobox(frame, textvariable=button_var, values=["Left", "Right"], state="readonly", width=5)
        button_dropdown.grid(row=0, column=2, padx=10, pady=5)
        button_dropdown.set("Left")

        def get_action():
            action = action_var.get()

            button = button_var.get()

            result = f"{action.split()[0]} {button} Mouse"
            self.add_option(result, '')

            new_window.destroy()

        ok_button = ttk.Button(frame, text="OK", command=get_action, width=18)
        ok_button.grid(row=1, column=0, padx=(0,20), pady=5)

        cancel_button = ttk.Button(frame, text="Cancel", command=new_window.destroy, width=18)
        cancel_button.place(y=36, x=125)
    
    
    def create_new_window_release_edit(self, index):
        new_window = tk.Toplevel(root)
        new_window.resizable(False, False)
        new_window.title("Choose Mouse Action")
        new_window.geometry("270x80")

        frame = ttk.Frame(new_window)
        frame.grid(row=0, column=0, padx=10, pady=10)

        action_var = tk.StringVar()

        action_dropdown = ttk.Combobox(frame, textvariable=action_var, values=["Hold Mouse", "Release Mouse"], state="readonly", width=18)
        action_dropdown.grid(row=0, column=0, padx=0, pady=5)
        action_dropdown.set("Release Mouse")

        label = ttk.Label(frame, text="Button")
        label.grid(row=0, column=1, padx=0, pady=5)

        button_var = tk.StringVar()
        
        button_dropdown = ttk.Combobox(frame, textvariable=button_var, values=["Left", "Right"], state="readonly", width=5)
        button_dropdown.grid(row=0, column=2, padx=10, pady=5)
        button_dropdown.set("Left")

        def get_action():
            action = action_var.get()

            button = button_var.get()

            result = f"{action.split()[0]} {button} Mouse"

            self.options[index] = (result, '')
            self.update_option_listbox()

            new_window.destroy()

        ok_button = ttk.Button(frame, text="OK", command=get_action, width=18)
        ok_button.grid(row=1, column=0, padx=(0,20), pady=5)

        cancel_button = ttk.Button(frame, text="Cancel", command=new_window.destroy, width=18)
        cancel_button.place(y=36, x=125)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)

    root.bind("<Control-q>", app.on_auto_move_position)
    root.mainloop()