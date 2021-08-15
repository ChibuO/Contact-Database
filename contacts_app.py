#database stuff for contacts list
#this is the code that only interacts with the user

#from same folder
from re import M, search
from tkinter.constants import BOTH, CENTER, END, LEFT, S, W
from tkinter import messagebox
import contacts_db
import tkinter.ttk as ttk
import tkinter as tk
from functools import partial

WIDTH = 650
HEIGHT = 360

BCK_COLOR = "lightblue"
BCK_COLOR2 = "#ebebeb" #silver
TEXT_COLOR = "black"
CARD_COLOR = "white"
BCK_COLOR3 = "#5FB691" #teal

#open database connection
connection = contacts_db.connect()
contacts_db.create_tables(connection)
#initial list of contacts
contacts = contacts_db.get_all_contacts(connection)

#make a scrollable frame class that i can use as a normal frame
#If you wanted to use this class, remember to place things inside self.scrollable_frame, 
# and not directly into an object of this class
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=230)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=CARD_COLOR)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=scrollbar.set, bg=CARD_COLOR)
        
        scrollbar.pack(side="right", fill="y", expand=0) #no expand
        self.canvas.pack(fill=tk.BOTH, expand=1)

#one entry card for the list
class ContactCard(tk.Frame):
    def __init__(self, parent, controller, id, fname, lname, major, year, state, met):
        tk.Frame.__init__(self, parent)
        self.configure(bg=BCK_COLOR2, bd=4, relief="groove")

        self.parent = parent
        self.controller = controller

        self.id = id
        self.fname = fname
        self.lname = lname
        self.major = major
        self.year = year
        self.state = state
        self.met = met

        if(self.lname and self.state):
            fullname = self.fname + " " + self.lname + " from " + self.state
        elif(self.lname and not self.state):
            fullname = self.fname + " " + self.lname
        elif(not self.lname and self.state):
            fullname = self.fname + " from " + self.state
        else:
            fullname = self.fname

        #based on what information is entered
        if(self.major and self.year):
            academic = self.major + " Major - Class of " + str(self.year)
        elif(self.major and not self.year):
            academic = self.major + " Major"
        elif(not self.major and self.year):
            academic = "Class of " + str(self.year)
        else:
            academic = "-"

        fullname_label = tk.Label(self, text=fullname, background=CARD_COLOR, anchor="w")
        academic_label = tk.Label(self, text=academic, bg=CARD_COLOR, anchor="w")
        met_label = tk.Label(self, text=("Met at " + self.met), bg=CARD_COLOR, anchor="w")

        fullname_label.pack(fill=tk.BOTH)
        academic_label.pack(fill=tk.BOTH)
        met_label.pack(fill=tk.BOTH)

        self.bind('<Double-Button>', self.ShowOptions)
        for child in self.winfo_children():
            child.bind('<Double-Button>', self.ShowOptions)

    def ShowOptions(self, event):
        card_info = (self.id, self.fname, self.lname, self.state, self.year, self.major, self.met)
        pop_up_width = 240
        pop_up_height = 100
        #center in window, add the position of the parent window
        pop_up_x = (WIDTH/2) - (pop_up_width/2) + self.controller.root.winfo_x()
        pop_up_y = (HEIGHT/2) - (pop_up_height/2) + self.controller.root.winfo_y()
        global pop_up
        pop_up = tk.Toplevel(self)
        pop_up.title("Options")
        pop_up.geometry(f"{pop_up_width}x{pop_up_height}+{int(pop_up_x)}+{int(pop_up_y)}")
        pop_up.configure(bg=BCK_COLOR3, pady=10, padx=10)
        pop_up.resizable(False, False)
        tk.Label(pop_up, text="What do you want to do?", bg=BCK_COLOR3).pack()

        my_frame = tk.Frame(pop_up, bg=BCK_COLOR3)
        my_frame.pack(pady=10)
        tk.Button(my_frame, text="Edit", command=lambda: self.choseOption("edit", card_info)).grid(row=0, column=0, padx=10)
        tk.Button(my_frame, text="Delete", command=lambda: self.choseOption("delete", card_info)).grid(row=0, column=1, padx=10)
        tk.Button(my_frame, text="Cancel", command=lambda: self.choseOption("cancel")).grid(row=0, column=2, padx=10)

    def choseOption(self, choice, card_info=()):
        #card info is a tuple with all the card values starting with the db id
        pop_up.destroy()
        #get the textboxes in the main application using controller
        if(choice == "edit"):
            textbox_tuple = self.controller.get_boxes()
            textbox_tuple[0].set(card_info[1]) #fname
            textbox_tuple[1].set(card_info[2]) #lname
            textbox_tuple[2].set(card_info[3]) #state
            textbox_tuple[3].set(card_info[4]) #year
            textbox_tuple[4].set(card_info[5]) #major
            textbox_tuple[5].set(card_info[6]) #met
            textbox_tuple[6].set(card_info[0]) #give id
        elif(choice == "delete"):
            del_confirm = messagebox.askyesno('Sure about that?', f'Are you sure you want to delete {card_info[1]} from {card_info[-1]}?') 
            if del_confirm == True:
                contacts_db.remove_contact(connection, card_info[0])
                global contacts
                contacts = contacts_db.get_all_contacts(connection)
                self.controller.rerender_list()
                print("deleted")
        else:
            print("canceled")
        
class ListFrame(ScrollableFrame):
    def __init__(self, parent, controller):
        ScrollableFrame.__init__(self, parent)

        self.controller = controller

        global contacts
        for index, name in enumerate(contacts):
            ContactCard(self.scrollable_frame, self.controller, name[0], name[1], name[2], name[3], name[4], name[5], name[6]).grid(row=index, column=0, pady=10, padx=10, sticky="ew")

class MainApplication(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        root.resizable(False, False)
        root.title("My Student List")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width/2) - WIDTH/2
        y = (screen_height/2) - HEIGHT/2 - 100
        root.geometry(f"{WIDTH}x{HEIGHT}+{int(x)}+{int(y)}")
        self.update_id = tk.StringVar()
        #main panel
        main_panel = tk.Frame(bg="yellow")
        main_panel.pack(expand=1, fill=tk.BOTH)
        
        #left panel - entry
        self.entry_panel = tk.Frame(main_panel, bg=BCK_COLOR, borderwidth = 1, relief="ridge")
        self.entry_panel.pack(fill=tk.BOTH, side=tk.LEFT)
        
        entry_title = tk.Label(self.entry_panel, text="Met Someone? ( * - Required )")
        entry_title.configure(bg=BCK_COLOR, foreground=TEXT_COLOR, padx=5, pady=10)

        entry_form = tk.Frame(self.entry_panel, bg=BCK_COLOR, padx=5)
        fname_label = tk.Label(entry_form, text="First Name *")
        self.fname = tk.StringVar()
        self.fname_textbox = tk.Entry(entry_form, width = 17, textvariable=self.fname)
        
        lname_label = tk.Label(entry_form, text="Last Name")
        self.lname = tk.StringVar()
        self.lname_textbox = tk.Entry(entry_form, width = 17, textvariable=self.lname)
        
        major_label = tk.Label(entry_form, text="Major")
        self.major = tk.StringVar()
        self.major_textbox = tk.Entry(entry_form, width = 30, textvariable=self.major)
        
        year_label = tk.Label(entry_form, text="Grad. Year")
        self.year = tk.StringVar()
        self.year_textbox = tk.Entry(entry_form, width = 17, textvariable=self.year)
        
        state_label = tk.Label(entry_form, text="Home City/State/Country")
        self.state = tk.StringVar()
        self.state_textbox = tk.Entry(entry_form, width = 20, textvariable=self.state)
        
        met_label = tk.Label(entry_form, text="Where did you meet? *")
        self.met = tk.StringVar()
        self.met_textbox = tk.Entry(entry_form, width = 50, textvariable=self.met)
        
        entry_title.pack(fill="x", side=tk.TOP)
        entry_form.pack(fill="x")
        fname_label.grid(column=0, row=1, sticky=tk.W)
        self.fname_textbox.grid(column=0, row=2, sticky=tk.W)
        lname_label.grid(column=1, row=1, sticky=tk.W)
        self.lname_textbox.grid(column=1, row=2, sticky=tk.W)
        state_label.grid(column=2, row=1, sticky=tk.W)
        self.state_textbox.grid(column=2, row=2, sticky=tk.W)
        year_label.grid(column=0, row=3, sticky=tk.W)
        self.year_textbox.grid(column=0, row=4, sticky=tk.W)
        major_label.grid(column=1, row=3, sticky=tk.W)
        self.major_textbox.grid(column=1, row=4, columnspan=2, sticky=tk.W)
        met_label.grid(column=0, row=5, sticky=tk.W, columnspan=3)
        self.met_textbox.grid(column=0, row=6, columnspan=3, sticky=tk.W)

        #3 equally spaced columns
        self.entry_panel.columnconfigure(0, weight=1)
        self.entry_panel.columnconfigure(1, weight=1)
        self.entry_panel.columnconfigure(2, weight=1)

        for child in entry_form.winfo_children():
            child.grid_configure(padx=5)
            if isinstance(child, tk.Entry):
                child.grid_configure(pady=(2, 20))
            if isinstance(child, tk.Label):
                child.configure(bg=BCK_COLOR, foreground=TEXT_COLOR)

        #add and  clear buttons in their own frame
        self.button_frame1 = tk.Frame(self.entry_panel, background=BCK_COLOR)
        
        self.add_btn = tk.Button(self.button_frame1, text="Add", command=partial(self.add_new_contact, connection))
        self.clear_btn = tk.Button(self.button_frame1, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        self.add_btn.pack(side=tk.RIGHT, padx=5)
        
        self.button_frame1.pack(fill="x")

        #right panel - list
        self.right_panel = tk.Frame(main_panel, bg=BCK_COLOR)
        self.right_panel.pack(fill="both", expand=1) #no expand so 
        
        list_title = tk.Label(self.right_panel, text="People I've Met", pady=10, borderwidth = 1, relief="ridge")
        list_title.pack(fill="x", side=tk.TOP)

        self.actual_list_frame = ListFrame(self.right_panel, self)
        self.actual_list_frame.pack(expand=1, fill=tk.BOTH)

        #frame with sorting option
        self.sort_frame = tk.Frame(self.right_panel, padx=10, pady=10, borderwidth = 1, relief="sunken")

        filter_label = tk.Label(self.sort_frame, text="Filter By: ", anchor="e")
        filter_label.pack(side="left", expand=1, fill="y")

        # Dropdown menu options
        sort_options = [
            "First Name", "Last Name",
            "State", "Major", "Year",
            "Met", "Date Added",
            "First Name (Reversed)", "Last Name (Reversed)",
            "State (Reversed)", "Major (Reversed)", "Year (Reversed)",
            "Met (Reversed)", "Date Added (Reversed)"
        ]

        # datatype of menu text
        self.sort_selection = tk.StringVar()

        drop = ttk.Combobox(self.sort_frame, textvariable=self.sort_selection, width=17)
        drop['values'] = sort_options
        drop['state'] = 'readonly'
        drop.current(0)
        drop.pack(side="left", expand=1, fill=tk.BOTH)
        drop.bind('<<ComboboxSelected>>', self.sort_contact_list)

        self.sort_frame.pack(expand=0, fill="x", side="bottom")

    def get_boxes(self):
        if self.button_frame1 is not None:
            self.button_frame1.destroy()
        
        #make ok and cancel buttons
        self.button_frame2 = tk.Frame(self.entry_panel, background=BCK_COLOR)
        self.edit_ok_btn = tk.Button(self.button_frame2, text="Ok", command=self.update_list)
        self.edit_cancel_button = tk.Button(self.button_frame2, text="Cancel", command=self.cancel_update)
        self.edit_cancel_button.pack(side=tk.RIGHT, padx=5)
        self.edit_ok_btn.pack(side=tk.RIGHT, padx=5)
        self.button_frame2.pack(fill="x")
        
        #return form in tuple
        return (self.fname, self.lname, self.state, self.year, self.major, self.met, self.update_id)

    def clear_form(self):
        self.fname_textbox.delete(0, tk.END)
        self.lname_textbox.delete(0, tk.END)
        self.major_textbox.delete(0, tk.END)
        self.year_textbox.delete(0, tk.END)
        self.state_textbox.delete(0, tk.END)
        self.met_textbox.delete(0, tk.END)

    def cancel_update(self):
        if self.button_frame2 is not None:
            self.button_frame2.destroy()
        
        #make new buttons after destroying them
        self.button_frame1 = tk.Frame(self.entry_panel, background=BCK_COLOR)
        self.add_btn = tk.Button(self.button_frame1, text="Add", command=partial(self.add_new_contact, connection))
        self.clear_btn = tk.Button(self.button_frame1, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        self.add_btn.pack(side=tk.RIGHT, padx=5)
        self.button_frame1.pack(fill="x")

        self.clear_form()

    def update_list(self):
        #make sure fname and met are filled and 
        if(not self.fname.get() or not self.met.get()):
            print("You must include a first name and the way you met.")
            return
        elif(self.year.get() and not self.year.get().isnumeric()):
            print("The year must be a number")
            return

        #if a year is entered, make it an int
        year_value = int(self.year.get()) if self.year.get() else ''
        #make id an int
        id_value = int(self.update_id.get())

        contacts_db.update_contact(connection, id_value, self.fname.get(), self.lname.get(), 
            self.major.get(), year_value, self.state.get(), self.met.get())
        
        global contacts
        contacts = contacts_db.get_all_contacts(connection)

        self.rerender_list()
        self.cancel_update()

    def add_new_contact(self, connection):
        #make sure fname and met are filled and 
        if(not self.fname.get() or not self.met.get()):
            print("You must include a first name and the way you met.")
            return
        elif(self.year.get() and not self.year.get().isnumeric()):
            print("The year must be a number")
            return

        #if a year is entered, make it an int
        year_value = int(self.year.get()) if self.year.get() else ''
        #else
        contacts_db.add_contact(connection, self.fname.get(), self.lname.get(), 
            self.major.get(), year_value, self.state.get(), self.met.get())

        global contacts
        contacts = contacts_db.get_all_contacts(connection)
        self.rerender_list()
        self.clear_form()

    def sort_contact_list(self, event):
        global contacts
        #if statements in contacts_db
        if("Reverse" in self.sort_selection.get()):
            updated_list = contacts_db.reverse_sort_by_field(connection, self.sort_selection.get())
            contacts = updated_list
            self.rerender_list()
            return

        #else
        if (self.sort_selection.get() == "First Name"):
            field = "fname"
        elif (self.sort_selection.get() == "Last Name"):
            field = "lname"
        elif (self.sort_selection.get() == "State"):
            field = "state"
        elif (self.sort_selection.get() == "Major"):
            field = "major"
        elif (self.sort_selection.get() == "Year"):
            field = "year"
        elif (self.sort_selection.get() == "Met"):
            field = "met"
        elif (self.sort_selection.get() == "Date Added"):
            field = "id"
        else:
            field = "id"
        
        updated_list = contacts_db.sort_by_field(connection, field)
        contacts = updated_list
        self.rerender_list()

    def rerender_list(self):
        if self.actual_list_frame is not None:
            self.actual_list_frame.destroy()
        self.actual_list_frame = ListFrame(self.right_panel, self)
        self.actual_list_frame.pack(expand=1, fill=tk.BOTH)

def see_all_contacts():
    #id. fname, lname, major, year, state, met
    print("\n~List~")
    global contacts
    for name in contacts:
        print(f"{name[0]}. {name[1]} {name[2]} from {name[5]}.\n{name[4]} in {name[3]}.\nMet at {name[6]}\n")
        #ex. 3. Jake from Deering

if __name__ == "__main__":
    #tkinter stuff
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()