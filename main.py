# Module main.py contains the Tkinter UI application: login, registration,
# book management, admin features, and user management.
from __future__ import annotations

import logging
from tkinter import *
from tkinter import messagebox, ttk
from typing import Any, Protocol, cast

from users import User
from books import Book

from logging_config import setup_logging

logger = logging.getLogger(__name__)


class PageFactory(Protocol):
    def __call__(self, parent: Widget, controller: Aplikacia) -> Frame: ...

# Login screen. Displays form fields for email and password.
class LoginPage(Frame):

    # Initializes login form with labels, inputs, and action buttons.
    # Inputs: parent (tk widget), controller (Aplikacia).
    # Returns: None.
    def __init__(self, parent: Widget, controller: Aplikacia) -> None:
        Frame.__init__(self, parent)
        self.controller = controller

        # Label
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
        logger.info("Login page initialized")

    # Validates login data and redirects by user role.
    # Shows an error message when authentication fails.
    # Inputs: user (str), passw (str).
    # Returns: None.
    def button_login(self, user: str, passw: str) -> None:
        if self.controller.user.authenticate(user, passw):
            logger.info("User authenticated successfully: email=%s role=%s", user, self.controller.user.role)
            if str(self.controller.user.role).strip() == "admin":
                self.controller.show_page(AdminPage)
            elif str(self.controller.user.role).strip() == "user":
                self.controller.show_page(BookManagement)
        else:
            messagebox.showerror("Prihlasenie", "Nespravne meno alebo heslo")
            logger.warning("Failed login attempt for email=%s", user)


# Book management - shared class for user/admin book table and borrowing actions.
class BookManagement(Frame):
    # Class for book operations: borrowing, returning, and table rendering.
    bd_input: Entry
    bn_input: Entry
    ba_input: Entry
    bi_input: Entry
    bc_input: ttk.Combobox

    # Initializes BookManagement with table and control widgets.
    # Inputs: parent (tk widget), controller (Aplikacia).
    # Returns: None.
    def __init__(self, parent: Widget, controller: Aplikacia) -> None:
        Frame.__init__(self, parent)
        self.controller = controller

        self.user_label = Label(
            self,
            text=f"User {self.controller.user.email} je prihlaseny ako {self.controller.user.role}",
            font=("Arial", 12, "bold"),
        )
        self.user_label.grid(column=0, row=0)
        self.user_label.config(padx=20, pady=20)
        logger.info(
            "BookManagement initialized for email=%s role=%s",
            self.controller.user.email,
            self.controller.user.role,
        )

        self._setup_books_table()
        self._setup_filter_controls()
        self.display_books_table()

    @staticmethod
    # Applies filters over a DataFrame by selected column and value.
    # Inputs: data (DataFrame), filter_name (str|None), filter_value (str|None),
    # column_map (dict), exact_match_columns (set|None).
    # Returns: pandas.DataFrame with filtered data.
    def apply_filters(
        data: Any,
        filter_name: str | None,
        filter_value: str | None,
        column_map: dict[str, str],
        exact_match_columns: set[str] | None = None,
    ) -> Any:
        normalized_filter = None if filter_name is None else str(filter_name).strip().lower()
        normalized_value = None if filter_value is None else str(filter_value).strip().lower()
        exact_match_columns = set() if exact_match_columns is None else set(exact_match_columns)

        if normalized_filter in column_map and normalized_value is not None:
            column = column_map[normalized_filter]
            logger.debug("Applying filter: column=%s value=%s", column, normalized_value)
            if column in exact_match_columns:
                return data[data[column].astype(str).str.strip().str.lower() == normalized_value]
            return data[data[column].astype(str).str.strip().str.lower().str.contains(normalized_value, na=False)]

        return data

    def _require_user_id(self) -> str:
        if self.controller.user.u_id is None:
            logger.warning("User ID required for action but not found: email=%s", self.controller.user.email)
            raise RuntimeError("User is not authenticated")

        return self.controller.user.u_id

    # Creates and configures the books table in UI.
    # Inputs: no inputs.
    # Returns: None.
    def _setup_books_table(self) -> None:
        self.table = ttk.Treeview(self)
        self.table['columns'] = (
            'ID',
            'Name',
            'Author',
            'ISBN',
            'Category',
            'State',
            'Borrow date',
            'Return date',
        )
        self.table.column('ID', width=60)
        self.table.column('Name', width=250)
        self.table.column('Author', width=180)
        self.table.column('ISBN', width=120)
        self.table.column('Category', width=110)
        self.table.column('State', width=75)
        self.table.column('Borrow date', width=100)
        self.table.column('Return date', width=100)

        # Hide 0th column
        self.table.column("#0", width=0, stretch=False)
        self.table.heading("#0", text="", anchor="w")

        self.table.heading('ID', text='ID')
        self.table.heading('Name', text='Name')
        self.table.heading('Author', text='Author')
        self.table.heading('ISBN', text='ISBN')
        self.table.heading('Category', text='Category')
        self.table.heading('State', text='State')
        self.table.heading('Borrow date', text='Borrow date')
        self.table.heading('Return date', text='Return date')
        self.table.tag_configure('oddrow', background='#E8E8E8')
        self.table.tag_configure('evenrow', background='#FFFFFF')

        self.table.grid(column=0, row=1, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.table.tag_configure('borrowedbyme', foreground='darkgreen')
        logger.debug("Books table configured")

    # Creates controls and buttons for filtering and book actions.
    # Inputs: no inputs.
    # Returns: None.
    def _setup_filter_controls(self) -> None:
        filter_buttons_frame = Frame(self)
        filter_buttons_frame.grid(column=0, row=2, pady=10, sticky="w")

        self.available_button = Button(
            filter_buttons_frame,
            text="Dostupné knihy",
            command=lambda: self.display_books_table("state", "0"),
        )
        self.available_button.grid(row=0, column=0, padx=5)

        self.unavailable_button = Button(
            filter_buttons_frame,
            text="Požicané knihy",
            command=lambda: self.display_books_table("state", "1"),
        )
        self.unavailable_button.grid(row=0, column=1, padx=5)

        self.all_books_button = Button(
            filter_buttons_frame,
            text="Všetky knihy",
            command=lambda: self.display_books_table(),
        )
        self.all_books_button.grid(row=0, column=2, padx=5)

        self.my_books_button = Button(
            filter_buttons_frame,
            text="Zobraz moje knihy",
            command=lambda: self.display_books_table("user", self._require_user_id()),
        )
        self.my_books_button.grid(row=0, column=3, padx=5)

        self.book_label = Label(filter_buttons_frame, text="Zadaj ID knihy", font=("Arial", 10))
        self.book_label.grid(row=1, column=0, padx=5)

        self.b_input = Entry(filter_buttons_frame, width=20)
        self.b_input.grid(row=1, column=1, padx=5)

        self.borrow_button = Button(filter_buttons_frame, text="Pozicat", command=self.borrow_clicked)
        self.borrow_button.grid(row=1, column=2, padx=5)

        self.return_button = Button(filter_buttons_frame, text="Vratit", command=self.return_clicked)
        self.return_button.grid(row=1, column=3, padx=5)

        self.extend_button = Button(
            filter_buttons_frame,
            text="Predlz pozicanie",
            command=self.extend_clicked,
        )
        self.extend_button.grid(row=1, column=4, padx=5)

        self.book_label1 = Label(filter_buttons_frame, text="Filtruj knihy podľa názvu", font=("Arial", 10))
        self.book_label1.grid(row=2, column=0, padx=5)

        self.name_input = Entry(filter_buttons_frame, width=20)
        self.name_input.grid(row=2, column=1, padx=5)

        self.searchname_button = Button(
            filter_buttons_frame,
            text="Vyhladaj",
            command=lambda: self.display_books_table("name", self.name_input.get()),
        )
        self.searchname_button.grid(row=2, column=2, padx=5)

        self.book_label3 = Label(filter_buttons_frame, text="Filtruj knihy podľa ISBN", font=("Arial", 10))
        self.book_label3.grid(row=3, column=0, padx=5)

        self.isbn_input = Entry(filter_buttons_frame, width=20)
        self.isbn_input.grid(row=3, column=1, padx=5)

        self.searchisbn_button = Button(
            filter_buttons_frame,
            text="Vyhladaj",
            command=lambda: self.display_books_table("isbn", self.isbn_input.get()),
        )
        self.searchisbn_button.grid(row=3, column=2, padx=5)

        self.book_label2 = Label(filter_buttons_frame, text="Filtruj knihy podľa autora", font=("Arial", 10))
        self.book_label2.grid(row=4, column=0, padx=5)

        self.author_input = Entry(filter_buttons_frame, width=20)
        self.author_input.grid(row=4, column=1, padx=5)

        self.searchauthor_button = Button(
            filter_buttons_frame,
            text="Vyhladaj",
            command=lambda: self.display_books_table("author", self.author_input.get()),
        )
        self.searchauthor_button.grid(row=4, column=2, padx=5)

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(column=0, row=99, pady=10, sticky="w")

        logger.info("Filter controls setup completed")

    # Renders book rows in the table and applies row styling.
    # Inputs: data (pandas.DataFrame).
    # Returns: None.
    def _render_books_table_rows(self, data: Any) -> None:
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
            self.table.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["name"],
                    row["author"],
                    row["isbn"],
                    row["category"],
                    state_display,
                    row["date"],
                    row["return_date"],
                ),
                tags=tags,
            )
            tags.clear()


    # Displays books table and optionally applies filtering.
    # If filter and filter_value are None, all books are shown.
    # Supported filters: name, author, isbn, state, category, user.
    # Inputs: filter (str|None), filter_value (str|None).
    # Returns: None.
    def display_books_table(self, filter: str | None = None, filter_value: str | None = None) -> None:
        data = Book.load_books_data()

        column_map = {
            "name": "name",
            "author": "author",
            "isbn": "isbn",
            "category": "category",
            "state": "state",
            "user": "user"
        }

        filtered_data = self.apply_filters(data, filter, filter_value, column_map, exact_match_columns={"user"})
        self._render_books_table_rows(filtered_data)
        logger.info("Books table displayed: rows=%s filter=%s", len(filtered_data), filter)

    # Handles click on Borrow button, borrows selected book and refreshes table.
    # Inputs: no inputs (reads value from self.b_input).
    # Returns: None.
    def borrow_clicked(self) -> None:
        book_id = self.b_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            logger.warning("Borrow failed: missing book_id")
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            logger.warning("Borrow failed: book_id=%s does not exist", book_id)
            return

        if book.borrow_book(self._require_user_id()):
            self.delete_data_table()
            self.update_data_table()
            logger.info("Book borrowed from UI: book_id=%s email=%s", book_id, self.controller.user.email)
        else:
            messagebox.showinfo("Chyba", "Kniha je uz pozicana")
            logger.warning("Borrow failed from UI: book_id=%s email=%s", book_id, self.controller.user.email)

    # Handles click on Return button, returns selected book and refreshes table.
    # Inputs: no inputs (reads value from self.b_input).
    # Returns: None.
    def return_clicked(self) -> None:
        book_id = self.b_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            logger.warning("Return failed: missing book_id")
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            logger.warning("Return failed: book_id=%s does not exist", book_id)
            return

        if book.return_book(self._require_user_id()):
            self.delete_data_table()
            self.update_data_table()
            logger.info("Book returned from UI: book_id=%s email=%s", book_id, self.controller.user.email)
        else:
            messagebox.showinfo("Chyba", "Kniha nie je pozicana alebo ju nemate pozicanu vy")
            logger.warning("Return failed from UI: book_id=%s email=%s", book_id, self.controller.user.email)

    # Handles click on Extend Borrowing button.
    # Inputs: no inputs (reads value from self.b_input).
    # Returns: None.
    def extend_clicked(self) -> None:
        book_id = self.b_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            logger.warning("Extend failed: missing book_id email=%s", self.controller.user.email)
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            logger.warning("Extend failed: book_id=%s does not exist email=%s", book_id, self.controller.user.email)
            return

        if book.extend_borrowing(self._require_user_id()):
            self.delete_data_table()
            self.update_data_table()
            messagebox.showinfo("Hotovo", "Doba pozicania bola predlzena o 14 dni")
            logger.info("Borrowing extended from UI: book_id=%s email=%s", book_id, self.controller.user.email)
        else:
            messagebox.showinfo("Chyba", "Kniha nie je pozicana alebo ju nemate pozicanu vy")
            logger.warning("Extend failed from UI: book_id=%s email=%s", book_id, self.controller.user.email)


    # Handles click on Delete button and deletes a book by ID.
    # Inputs: no inputs (reads value from self.bd_input).
    # Returns: None.
    def delete_clicked(self) -> None:
        book_id = self.bd_input.get().strip()
        if not book_id:
            messagebox.showerror("Chyba", "Zadaj ID knihy")
            logger.warning("Delete failed: missing book_id email=%s", self.controller.user.email)
            return

        book = Book(book_id)

        if book.name is None:
            messagebox.showerror("Chyba", "Kniha s tymto ID neexistuje")
            logger.warning("Delete failed: book_id=%s does not exist email=%s", book_id, self.controller.user.email)
            return

        book.delete_book()
        self.delete_data_table()
        self.update_data_table()
        logger.info("Book deleted from UI: book_id=%s email=%s", book_id, self.controller.user.email)
        messagebox.showinfo("Hotovo", "Kniha bola vymazana")

    # Handles adding a new book after input validation.
    # Inputs: no inputs (reads values from form fields).
    # Returns: None.
    def add_clicked(self) -> None:
        name = self.bn_input.get().strip()
        author = self.ba_input.get().strip()
        isbn = self.bi_input.get().strip()
        category = self.bc_input.get().strip()

        if not name or not author or not isbn or not category:
            messagebox.showerror("Chyba", "Vypln nazov, autora, ISBN aj kategoriu")
            logger.warning("Add book failed: missing required fields")
            return

        if category not in Book.get_categories():
            messagebox.showerror("Chyba", "Vyber kategoriu zo zoznamu")
            logger.warning("Add book failed: invalid category=%s", category)
            return

        data = Book.load_books_data()
        existing_isbn = data['isbn'].astype(str).str.strip()

        if isbn in existing_isbn.values:
            messagebox.showerror("Chyba", "Kniha uz je v databaze")
            logger.warning("Add book failed: duplicate isbn=%s", isbn)
            return

        Book.add_book(name, author, isbn, category)

        self.delete_data_table()
        self.update_data_table()
        logger.info("Book added from UI: name=%s isbn=%s category=%s", name, isbn, category)
        messagebox.showinfo("Hotovo", "Kniha bola pridana")

    # Refreshes current books table data.
    # Inputs: no inputs.
    # Returns: None.
    def update_data_table(self) -> None:
        self.display_books_table()

    # Deletes all rows from the books table.
    # Inputs: no inputs.
    # Returns: None.
    def delete_data_table(self) -> None:
        for line in self.table.get_children():
            self.table.delete(line)

# Registration screen for new users.
class RegPage(Frame):

    # Initializes the registration page.
    # Inputs: parent (tk widget), controller (Aplikacia).
    # Returns: None.
    def __init__(self, parent: Widget, controller: Aplikacia) -> None:
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

    # Handles user registration and displays UI feedback.
    # Inputs: no inputs (reads values from registration form).
    # Returns: None.
    def register_clicked(self) -> None:
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
            logger.info("Registration succeeded: email=%s", email)
            self.controller.show_page(LoginPage)
        else:
            messagebox.showerror("Chyba", msg)
            logger.warning("Registration failed: email=%s reason=%s", email, msg)

# AdminPage extends book management with admin actions (add/delete/users).
class AdminPage(BookManagement):

    # Initializes the admin page by extending BookManagement.
    # Inputs: parent (tk widget), controller (Aplikacia).
    # Returns: None.
    def __init__(self, parent: Widget, controller: Aplikacia) -> None:
        super().__init__(parent, controller)

        # Admin control block.
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

        self.book_label = Label(filter_frame, text="Vyber kategoriu", font=("Arial", 10))
        self.book_label.grid(row=7, column=0, padx=5)

        self.bc_input = ttk.Combobox(filter_frame, width=18, values=Book.get_categories(), state="readonly")
        self.bc_input.grid(row=7, column=1, padx=5)

        self.add_button = Button(filter_frame, text="Pridaj", command=self.add_clicked)
        self.add_button.grid(row=7, column=2, padx=5)

        self.user_mgmt_button = Button(
            filter_frame,
            text="User Management",
            command=lambda: self.controller.show_page(UserManagementPage),
        )
        self.user_mgmt_button.grid(row=98, column=0, padx=5)

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(row=99, column=0, pady=10, sticky="w")
        logger.info("Admin page initialized for email=%s", self.controller.user.email)

# UserManagementPage manages user list, filtering, and deletion.
class UserManagementPage(Frame):
    # Initializes user management page.
    # Inputs: parent (tk widget), controller (Aplikacia).
    # Returns: None.
    def __init__(self, parent: Widget, controller: Aplikacia) -> None:
        Frame.__init__(self, parent)
        self.controller = controller

        filter_frame = Frame(self)
        filter_frame.grid(column=0, row=2, pady=10, sticky="w")

        self.show_user_table()

        self.iddel_label = Label(filter_frame, text="Zadaj ID usera na vymazanie", font=("Arial", 10))
        self.iddel_label.grid(row=0, column=0, padx=5)

        self.iddel_input = Entry(filter_frame, width=20)
        self.iddel_input.grid(row=0, column=1, padx=5)

        self.delete_button = Button(
            filter_frame,
            text="Vymaz",
            command=lambda: self.delete_clicked(self.iddel_input.get()),
        )
        self.delete_button.grid(row=0, column=2, padx=5)

        self.delete_button = Button(filter_frame, text="Zobraz vsetkuch userov", command=self.show_user_table)
        self.delete_button.grid(row=0, column=3, padx=5)

        self.id_label = Label(filter_frame, text="Filtruj userov podľa ID", font=("Arial", 10))
        self.id_label.grid(row=1, column=0, padx=5)

        self.id_input = Entry(filter_frame, width=20)
        self.id_input.grid(row=1, column=1, padx=5)

        self.id_button = Button(
            filter_frame,
            text="Vyhladaj",
            command=lambda: self.show_user_table("id", self.id_input.get()),
        )
        self.id_button.grid(row=1, column=2, padx=5)

        self.user_label = Label(filter_frame, text="Filtruj userov podľa mena", font=("Arial", 10))
        self.user_label.grid(row=2, column=0, padx=5)

        self.user_label_input = Entry(filter_frame, width=20)
        self.user_label_input.grid(row=2, column=1, padx=5)

        self.user_label_button = Button(
            filter_frame,
            text="Vyhladaj",
            command=lambda: self.show_user_table("name", self.user_label_input.get()),
        )
        self.user_label_button.grid(row=2, column=2, padx=5)

        self.back_button = Button(
            self,
            text="Spat na Book Management",
            command=lambda: self.controller.show_page(AdminPage),
        )
        self.back_button.grid(row=99, column=1, pady=10, padx=5, sticky="w")

        self.logout_button = Button(self, text="Odhlasit", command=self.controller.logout)
        self.logout_button.grid(row=99, column=0, pady=10, sticky="w")
        logger.info("User management page initialized")

    # Deletes a user by ID and refreshes table view.
    # Inputs: user_id (str|int).
    # Returns: None.
    def delete_clicked(self, user_id: str | int) -> None:
        user_id = str(user_id).strip()
        if not user_id:
            messagebox.showerror("Chyba", "Zadaj ID usera")
            logger.warning("User delete failed: missing user_id")
            return

        data = User.load_users_data()
        data['id'] = data['id'].str.strip()

        if user_id not in data['id'].values:
            messagebox.showerror("Chyba", "User s tymto ID neexistuje")
            logger.warning("User delete failed: user_id=%s not found", user_id)
            return

        data = data[data['id'] != str(user_id)]
        data.to_csv("logins.csv", index=False)
        messagebox.showinfo("Hotovo", "User bol vymazany")
        logger.info("User deleted from UI: user_id=%s", user_id)
        if UserManagementPage in self.controller.frames:
            self.controller.frames[UserManagementPage].destroy()
            del self.controller.frames[UserManagementPage]
        self.controller.show_page(UserManagementPage)

    # Displays users table with optional filtering.
    # Inputs: filter_name (str|None), filter_value (str|None).
    # Returns: None.
    def show_user_table(self, filter_name: str | None = None, filter_value: str | None = None) -> None:
        data = User.load_users_data()

        self.label = Label(
            self,
            text=f"Admin User Management ({self.controller.user.email})",
            font=("Arial", 24, "bold"),
        )
        self.label.grid(column=0, row=0)
        self.label.config(padx=20, pady=20)

        self.table = ttk.Treeview(self)
        self.table['columns'] = ('ID', 'Email', 'Name', 'Role')
        self.table.column('ID', width=60)
        self.table.column('Email', width=300)
        self.table.column('Name', width=200)
        self.table.column('Role', width=100)

        # Hide 0th column
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
        logger.info("User table displayed: rows=%s filter=%s", len(filtered_data), filter_name)

        tags = []
        for row_index, (_, row) in enumerate(filtered_data.iterrows()):
            if self.controller.user.u_id == row["id"]:
                tags.append('borrowedbyme')
            if row_index % 2 == 0:
                tags.append('evenrow')
            else:
                tags.append('oddrow')

            self.table.insert(
                "",
                "end",
                values=(row["id"], row["email"], row["name"], row["role"]),
                tags=tags,
            )
            tags.clear()

# Main application class. Handles page navigation and logged-in user state.
class Aplikacia(Tk):

    # Initializes the main window, title, size, and initial login page.
    # Inputs: *args, **kwargs (Tk arguments).
    # Returns: None.
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        Tk.__init__(self, *args, **kwargs)
        self.title("Library App")
        self.geometry("1200x700")
        self.config(padx=20, pady=20)
        self.user = User()

        self.container = Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.frames: dict[type[Frame], Frame] = {}

        self.show_page(LoginPage)
        logger.info("Application initialized")

    # Displays requested page (Frame). Creates and caches it if needed.
    # Inputs: page (Frame class).
    # Returns: None.
    def show_page(self, page: type[Frame]) -> None:
        if page not in self.frames:
            frame = cast(PageFactory, page)(self.container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            logger.debug("Page created: %s", page.__name__)

        frame = self.frames[page]
        frame.tkraise()
        logger.info("Page shown: %s", page.__name__)

    # Logs out user, clears cached pages, and returns to LoginPage.
    # Inputs: no inputs.
    # Returns: None.
    def logout(self) -> None:
        logger.info("Logout started: email=%s", self.user.email)
        for page in list(self.frames.keys()):
            if page != LoginPage:
                self.frames[page].destroy()
                del self.frames[page]
        self.user = User()
        self.show_page(LoginPage)
        logger.info("Logout completed")


setup_logging()
app = Aplikacia()
app.mainloop()
