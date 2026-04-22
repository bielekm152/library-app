from tkinter import *
from tkinter import messagebox, ttk

from users import User
from books import Book

# Prihlasovacia obrazovka. Zobrazuje formulár na zadanie e-mailu a hesla.
class LoginPage(Frame):

    # Inicializuje prihlasovací formulár s labelmi, vstupmi a tlačidlami.
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #Label
        self.my_label = Label(self, text="Login", font=("Arial", 24, "bold"))
        self.my_label.grid(column=0, row=0)
        self.my_label.config(padx=20, pady=20)

        self.username = Label(self, text="E-mail", font=("Arial", 10))
        self.username.grid(column=0, row=1, sticky= NW)

        self.u_input = Entry(self, width=20)
        self.u_input.grid(column=0,row=2)

        self.password = Label(self, text="Heslo", font=("Arial", 10))
        self.password.grid(column=0, row=4, sticky= NW)

        self.p_input = Entry(self, width=20, show="*")
        self.p_input.grid(column=0,row=5)

        self.login_button = Button(
            self,
            text = "Prihlasit",
            command = lambda: self.button_login(self.u_input.get() ,self.p_input.get())
        )

        self.login_button.grid(column=0, row=6, pady=10)

        self.reg_button = Button(
            self,
            text = "Registrovat",
            command= lambda: self.controller.show_page(RegPage)
        )

        self.reg_button.grid(column=0, row=7, pady=10)

    # Overí prihlasovacie údaje. Pri úspechu presmeruje na AdminPage alebo BookManagement podľa roly.
    # Pri neúspechu zobrazí chybovú správu.
    def button_login(self, user, passw):
        if self.controller.user.authenticate(user, passw):
            if str(self.controller.user.role).strip() == "admin":
                self.controller.show_page(AdminPage)   
            elif str(self.controller.user.role).strip() == "user":
                self.controller.show_page(BookManagement)
        else:
            messagebox.showerror("Prihlasenie", "Nespravne meno alebo heslo")


# Správa kníh - zdieľaná trieda pre BookManagement a AdminPage s tabuľkou a požičiavacím systémom.
class BookManagement(Frame):
    # Trieda na správu kníh - požičiavanie, vrátenie a zobrazenie tabuľky.

    # Inicializuje BookManagement s tabuľkou kníh a ovládacími prvkami.
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.user_label = Label(self, text=f"User {self.controller.user.email} je prihlaseny ako {self.controller.user.role}", font=("Arial", 12, "bold"))
        self.user_label.grid(column=0, row=0)
        self.user_label.config(padx=20, pady=20)

        self._setup_books_table()
        self._setup_filter_controls()
        self.display_books_table()

    @staticmethod
    def apply_filters(data, filter_name, filter_value, column_map, exact_match_columns=None):
        normalized_filter = None if filter_name is None else str(filter_name).strip().lower()
        normalized_value = None if filter_value is None else str(filter_value).strip().lower()
        exact_match_columns = set() if exact_match_columns is None else set(exact_match_columns)

        if normalized_filter in column_map and normalized_value is not None:
            column = column_map[normalized_filter]
            if column in exact_match_columns:
                return data[data[column].astype(str).str.strip().str.lower() == normalized_value]
            return data[data[column].astype(str).str.strip().str.lower().str.contains(normalized_value, na=False)]

        return data
    


    def _setup_books_table(self):
        self.table = ttk.Treeview(self)
        self.table['columns'] = ('ID', 'Name', 'Author', 'ISBN', 'State', 'Borrow date', 'Return date')
        self.table.column('ID', width=60)
        self.table.column('Name', width=300)
        self.table.column('Author', width=200)
        self.table.column('ISBN', width=120)
        self.table.column('State', width=75)
        self.table.column('Borrow date', width=100)
        self.table.column('Return date', width=100)

        # HIDE 0th Column
        self.table.column("#0", width=0, stretch=False)
        self.table.heading("#0", text="", anchor="w")

        self.table.heading('ID', text='ID')
        self.table.heading('Name', text='Name')
        self.table.heading('Author', text='Author')
        self.table.heading('ISBN', text='ISBN')
        self.table.heading('State', text='State')
        self.table.heading('Borrow date', text='Borrow date')
        self.table.heading('Return date', text='Return date')
        self.table.tag_configure('oddrow', background='#E8E8E8')
        self.table.tag_configure('evenrow', background='#FFFFFF')

        self.table.grid(column=0, row=1, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.table.tag_configure('borrowedbyme', foreground='darkgreen')

    def _setup_filter_controls(self):
        filter_buttons_frame = Frame(self)
        filter_buttons_frame.grid(column=0, row=2, pady=10, sticky="w")

        self.available_button = Button(filter_buttons_frame, text="Dostupné knihy", command=lambda: self.display_books_table("state", "0"))
        self.available_button.grid(row=0, column=0, padx=5)

        self.unavailable_button = Button(filter_buttons_frame, text="Požicané knihy", command=lambda: self.display_books_table("state", "1"))
        self.unavailable_button.grid(row=0, column=1, padx=5)

        self.all_books_button = Button(filter_buttons_frame, text="Všetky knihy", command=lambda: self.display_books_table())
        self.all_books_button.grid(row=0, column=2, padx=5)

        self.my_books_button = Button(filter_buttons_frame, text="Zobraz moje knihy", command=lambda: self.display_books_table("user", self.controller.user.u_id))
        self.my_books_button.grid(row=0, column=3, padx=5)

        self.book_label = Label(filter_buttons_frame, text="Zadaj ID knihy", font=("Arial", 10))
        self.book_label.grid(row=1, column=0, padx=5)

        self.b_input = Entry(filter_buttons_frame, width=20)
        self.b_input.grid(row=1, column=1, padx=5)

        self.borrow_button = Button(filter_buttons_frame, text="Pozicat", command=self.borrow_clicked)
        self.borrow_button.grid(row=1, column=2, padx=5)

        self.return_button = Button(filter_buttons_frame, text="Vratit", command=self.return_clicked)
        self.return_button.grid(row=1, column=3, padx=5)

        self.book_label1 = Label(filter_buttons_frame, text="Filtruj knihy podľa názvu", font=("Arial", 10))
        self.book_label1.grid(row=2, column=0, padx=5)

        self.name_input = Entry(filter_buttons_frame, width=20)
        self.name_input.grid(row=2, column=1, padx=5)

        self.searchname_button = Button(filter_buttons_frame, text="Vyhladaj", command=lambda: self.display_books_table("name", self.name_input.get()))
        self.searchname_button.grid(row=2, column=2, padx=5)

        self.book_label3 = Label(filter_buttons_frame, text="Filtruj knihy podľa ISBN", font=("Arial", 10))
        self.book_label3.grid(row=3, column=0, padx=5)

        self.isbn_input = Entry(filter_buttons_frame, width=20)
        self.isbn_input.grid(row=3, column=1, padx=5)

        self.searchisbn_button = Button(filter_buttons_frame, text="Vyhladaj", command=lambda: self.display_books_table("isbn", self.isbn_input.get()))
        self.searchisbn_button.grid(row=3, column=2, padx=5)

        self.book_label2 = Label(filter_buttons_frame, text="Filtruj knihy podľa autora", font=("Arial", 10))
        self.book_label2.grid(row=4, column=0, padx=5)

        self.author_input = Entry(filter_buttons_frame, width=20)
        self.author_input.grid(row=4, column=1, padx=5)

        self.searchauthor_button = Button(filter_buttons_frame, text="Vyhladaj", command=lambda: self.display_books_table("author", self.author_input.get()))
        self.searchauthor_button.grid(row=4, column=2, padx=5)

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(column=0, row=99, pady=10, sticky="w")

    def _render_books_table_rows(self, data):
        self.delete_data_table()

        tags = []
        for row_index, (_, row) in enumerate(data.iterrows()):
            if self.controller.user.u_id == row["user"]:
                tags.append('borrowedbyme')
            if row_index % 2 == 0:
                tags.append('evenrow')
            else:
                tags.append('oddrow')

            state_display = "dostupné" if row["state"] == 0 else "požičané"
            self.table.insert("", "end", values=(row["id"], row["name"], row["author"], row["isbn"], state_display, row["date"], row["return_date"]), tags=tags)
            tags.clear()

    # Vytvorí tabuľku kníh a voliteľne ju vyfiltruje.
    # Ak sú filter aj filter_value None, zobrazí všetky knihy.
    # Podporované filtre: name, author, isbn, state.
    def display_books_table(self, filter=None, filter_value=None):
        data = Book.load_books_data()

        column_map = {
            "name": "name",
            "author": "author",
            "isbn": "isbn",
            "state": "state",
            "user": "user"
        }

        filtered_data = self.apply_filters(data, filter, filter_value, column_map, exact_match_columns={"user"})
        self._render_books_table_rows(filtered_data)

    # Spracuje kliknutie na tlačidlo Požičať. Načíta ID knihy zo vstupu,
    # pokúsi sa o požičanie a aktualizuje tabuľku.
    def borrow_clicked(self):
        book_id = self.b_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            return

        if book.borrow_book(self.controller.user.u_id):
            self.delete_data_table()
            self.update_data_table()
        else:
            messagebox.showinfo("Chyba", "Kniha je uz pozicana")

    # Spracuje kliknutie na tlačidlo Vrátiť. Načíta ID knihy zo vstupu,
    # pokúsi sa o vrátenie a aktualizuje tabuľku.
    def return_clicked(self):
        book_id = self.b_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            return

        if book.return_book(self.controller.user.u_id):
            self.delete_data_table()
            self.update_data_table()
        else:
            messagebox.showinfo("Chyba", "Kniha nie je pozicana alebo ju nemate pozicanu vy")
        

    def delete_clicked(self):
        book_id = self.bd_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            return

        book.delete_book()
        self.delete_data_table()
        self.update_data_table()
        messagebox.showinfo("Hotovo", "Kniha bola vymazana")

    def add_clicked(self):
        name = self.bn_input.get().strip()
        author = self.ba_input.get().strip()
        isbn = self.bi_input.get().strip()

        if not name or not author or not isbn:
            messagebox.showerror("Chyba", "Vypln nazov, autora aj ISBN")
            return

        data = Book.load_books_data()
        existing_isbn = data['isbn'].astype(str).str.strip()

        if isbn in existing_isbn.values:
            messagebox.showerror("Chyba", "Kniha uz je v databaze")
            return

        Book.add_book(name, author, isbn)

        self.delete_data_table()
        self.update_data_table()
        messagebox.showinfo("Hotovo", "Kniha bola pridana")
    
    # Načíta dáta z books.csv a naplní tabuľku riadkami. Knihy požičané
    # aktuálnym používateľom sú zvýraznené zelenou farbou.
    def update_data_table(self):
        self.display_books_table()

    # Vymaže všetky riadky z tabuľky kníh.
    def delete_data_table(self):
        for line in self.table.get_children():
            self.table.delete(line)

# Registračná obrazovka pre nových používateľov.
class RegPage(Frame):

    # Inicializuje registračnú stránku.
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.reg_label = Label(self, text="Registracia", font=("Arial", 24, "bold"))
        self.reg_label.grid(column=0, row=0)
        self.reg_label.config(padx=20, pady=20)

        self.name_label = Label(self, text="Meno", font=("Arial", 10))
        self.name_label.grid(column=0, row=1, sticky=NW)
        self.name_input = Entry(self, width=30)
        self.name_input.grid(column=0, row=2, pady=(0, 8), sticky=W)

        self.email_label = Label(self, text="E-mail", font=("Arial", 10))
        self.email_label.grid(column=0, row=3, sticky=NW)
        self.email_input = Entry(self, width=30)
        self.email_input.grid(column=0, row=4, pady=(0, 8), sticky=W)

        self.password_label = Label(self, text="Heslo", font=("Arial", 10))
        self.password_label.grid(column=0, row=5, sticky=NW)
        self.password_input = Entry(self, width=30, show="*")
        self.password_input.grid(column=0, row=6, pady=(0, 8), sticky=W)

        self.register_button = Button(self, text="Vytvorit ucet", command=self.register_clicked)
        self.register_button.grid(column=0, row=7, pady=5, sticky=W)

        self.back_button = Button(self, text="Spat na login", command=lambda: self.controller.show_page(LoginPage))
        self.back_button.grid(column=0, row=8, pady=5, sticky=W)

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(column=0, row=99, pady=10, sticky="w")

    def register_clicked(self):
        name = self.name_input.get().strip()
        email = self.email_input.get().strip()
        password = self.password_input.get().strip()
        role = "user"

        ok, msg = self.controller.user.create_user(email, password, name, role)
        if ok:
            messagebox.showinfo("Registracia", msg)
            self.name_input.delete(0, END)
            self.email_input.delete(0, END)
            self.password_input.delete(0, END)
            self.controller.show_page(LoginPage)
        else:
            messagebox.showerror("Chyba", msg)

class AdminPage(BookManagement):

    # Inicializuje admin stránku dedením z BookManagement.
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Tlačidlá na filtrovanie kníh
        filter_frame = Frame(self)
        filter_frame.grid(column=0, row=3, pady=10, sticky="w")

        self.book_label = Label(filter_frame, text="Zadaj ID knihy", font=("Arial", 10))
        self.book_label.grid(row=5, column=0, padx=5)

        self.bd_input = Entry(filter_frame, width=20)
        self.bd_input.grid(row=5, column=1, padx=5)

        self.delete_button = Button(filter_frame, text="Vymaz", command=self.delete_clicked)
        self.delete_button.grid(row=5, column=2, padx=5)

        self.book_label = Label(filter_frame, text="Zadaj nazov knihy", font=("Arial", 10))
        self.book_label.grid(row=6, column=0, padx=5)

        self.bn_input = Entry(filter_frame, width=20)
        self.bn_input.grid(row=6, column=1, padx=5)

        self.book_label = Label(filter_frame, text="Zadaj autora knihy", font=("Arial", 10))
        self.book_label.grid(row=6, column=2, padx=5)

        self.ba_input = Entry(filter_frame, width=20)
        self.ba_input.grid(row=6, column=3, padx=5)

        self.book_label = Label(filter_frame, text="Zadaj ISBN knihy", font=("Arial", 10))
        self.book_label.grid(row=6, column=4, padx=5)

        self.bi_input = Entry(filter_frame, width=20)
        self.bi_input.grid(row=6, column=5, padx=5)

        self.add_button = Button(filter_frame, text="Pridaj", command=self.add_clicked)
        self.add_button.grid(row=6, column=6, padx=5)

        self.user_mgmt_button = Button(filter_frame, text="User Management", command=lambda: self.controller.show_page(UserManagementPage))
        self.user_mgmt_button.grid(row=98, column=0, padx=5)

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(row=99, column=0, pady=10, sticky="w")

class UserManagementPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        filter_frame = Frame(self)
        filter_frame.grid(column=0, row=2, pady=10, sticky="w")

        self.show_user_table()

        self.iddel_label = Label(filter_frame, text="Zadaj ID usera na vymazanie", font=("Arial", 10))
        self.iddel_label.grid(row=0, column=0, padx=5)

        self.iddel_input = Entry(filter_frame, width=20)
        self.iddel_input.grid(row=0, column=1, padx=5)

        self.delete_button = Button(filter_frame, text="Vymaz", command=lambda: self.delete_clicked(self.iddel_input.get()))
        self.delete_button.grid(row=0, column=2, padx=5)

        self.delete_button = Button(filter_frame, text="Zobraz vsetkuch userov", command=self.show_user_table)
        self.delete_button.grid(row=0, column=3, padx=5)

        self.id_label = Label(filter_frame, text="Filtruj userov podľa ID", font=("Arial", 10))
        self.id_label.grid(row=1, column=0, padx=5)

        self.id_input = Entry(filter_frame, width=20)
        self.id_input.grid(row=1, column=1, padx=5)

        self.id_button = Button(filter_frame, text="Vyhladaj", command=lambda: self.show_user_table("id", self.id_input.get()))
        self.id_button.grid(row=1, column=2, padx=5)

        self.user_label = Label(filter_frame, text="Filtruj userov podľa mena", font=("Arial", 10))
        self.user_label.grid(row=2, column=0, padx=5)

        self.user_label_input = Entry(filter_frame, width=20)
        self.user_label_input.grid(row=2, column=1, padx=5)

        self.user_label_button = Button(filter_frame, text="Vyhladaj", command=lambda: self.show_user_table("name", self.user_label_input.get()))
        self.user_label_button.grid(row=2, column=2, padx=5)

        self.back_button = Button(self, text="Spat na Book Management", command=lambda: self.controller.show_page(AdminPage))
        self.back_button.grid(row=99, column=1, pady=10, padx=5, sticky="w")

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(row=99, column=0, pady=10, sticky="w")

    def delete_clicked(self, user_id):
        user_id = str(user_id).strip()
        if not user_id:
            messagebox.showerror("Chyba", "Zadaj ID usera")
            return

        data = User.load_users_data()
        data['id'] = data['id'].str.strip()

        if user_id not in data['id'].values:
            messagebox.showerror("Chyba", "User s tymto ID neexistuje")
            return

        data = data[data['id'] != str(user_id)]
        data.to_csv("logins.csv", index=False)
        messagebox.showinfo("Hotovo", "User bol vymazany")
        if UserManagementPage in self.controller.frames:
            self.controller.frames[UserManagementPage].destroy()
            del self.controller.frames[UserManagementPage]
        self.controller.show_page(UserManagementPage)

    def show_user_table(self, filter_name=None, filter_value=None):
        data = User.load_users_data()

        self.label = Label(self, text=f"Admin User Management ({self.controller.user.email})", font=("Arial", 24, "bold"))
        self.label.grid(column=0, row=0)
        self.label.config(padx=20, pady=20)

        self.table = ttk.Treeview(self)
        self.table['columns'] = ('ID', 'Email', 'Name', 'Role')
        self.table.column('ID', width=60)
        self.table.column('Email', width=300)
        self.table.column('Name', width=200)
        self.table.column('Role', width=100)

        # HIDE 0th Column
        self.table.column("#0", width=0, stretch=False)
        self.table.heading("#0", text="", anchor="w")

        self.table.heading('ID', text='ID')
        self.table.heading('Email', text='Email')
        self.table.heading('Name', text='Name')
        self.table.heading('Role', text='Role')
        self.table.grid(column=0, row=1, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        column_map = {
            "id": "id",
            "email": "email",
            "name": "name",
            "role": "role"
        }

        filtered_data = BookManagement.apply_filters(
            data,
            filter_name,
            filter_value,
            column_map,
            exact_match_columns={"id"}
        )

        tags = []
        for row_index, (_, row) in enumerate(filtered_data.iterrows()):
            if self.controller.user.u_id == row["id"]:
                tags.append('borrowedbyme')
            if row_index % 2 == 0:
                tags.append('evenrow')
            else:
                tags.append('oddrow')

            self.table.insert("", "end", values=(row["id"], row["email"], row["name"], row["role"]), tags=tags)
            tags.clear()

# Hlavná trieda aplikácie. Riadi prepínanie medzi obrazovkami a uchováva stav prihláseného používateľa.
class Aplikacia(Tk):

    # Inicializuje hlavné okno aplikácie, nastaví titulok, veľkosť a zobrazí prihlasovaciu stránku.
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Library App")
        self.geometry("1000x600")
        self.config(padx=20, pady=20)
        self.user = User()

        self.container = Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.frames = {}

        self.show_page(LoginPage)

    # Zobrazí požadovanú stránku (Frame). Ak stránka ešte neexistuje, vytvorí ju a uloží do cache.
    def show_page(self, page):
        if page not in self.frames:
            frame = page(self.container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[page]
        frame.tkraise()

    # Odhlási používateľa, vymaže cache stránok a vráti na LoginPage.
    def logout(self):
        for page in list(self.frames.keys()):
            if page != LoginPage:
                self.frames[page].destroy()
                del self.frames[page]
        self.user = User()
        self.show_page(LoginPage)

    

app = Aplikacia()
app.mainloop()