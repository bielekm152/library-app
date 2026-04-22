from datetime import datetime
import pandas

BOOKS_DTYPE = {'id': str, 'name': str, 'author': str, 'isbn': str, 'state': int, 'date': str, 'user': str, 'return_date': str}

class Book:
    def __init__(self, book_id=None):
        self.id = book_id
        self.author = None
        self.isbn = None
        self.name = None
        self.state = None
        self.date = None
        self.user = None
        self.return_date = None
        if self.id is not None:
            self.define_book()

    @staticmethod
    def load_books_data():
        return pandas.read_csv("books.csv", dtype=BOOKS_DTYPE)

    def define_book(self):
        data = Book.load_books_data()

        data['id'] = data['id'].str.strip()

        mask = (data['id'] == str(self.id))
        filtered_data = data[mask]

        if not filtered_data.empty:
            self.name = str(filtered_data['name'].iloc[0])
            self.author = str(filtered_data['author'].iloc[0])
            self.isbn = str(filtered_data['isbn'].iloc[0])
            self.state = int(filtered_data['state'].iloc[0])
            self.date = str(filtered_data['date'].iloc[0])
            self.user = str(filtered_data['user'].iloc[0])
            self.return_date = str(filtered_data['return_date'].iloc[0])

    def borrow_book(self, user_id):
        if self.state == 0:
            now = datetime.now()
            data = Book.load_books_data()
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 1
            data.loc[mask, 'date'] = now.strftime('%d-%m-%Y')
            data.loc[mask, 'user'] = user_id
            data.loc[mask, 'return_date'] = (now + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')   

            data.to_csv("books.csv", index=False)
            self.state = 1
            self.date = now.strftime('%d-%m-%Y')
            self.return_date = (now + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')
            return True
        else:
            return False
        
    def return_book(self, user):
        if self.state == 1 and self.user == user:
            data = Book.load_books_data()
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 0
            data.loc[mask, 'date'] = '-'
            data.loc[mask, 'user'] = '-'
            data.loc[mask, 'return_date'] = '-'

            data.to_csv("books.csv", index=False)
            self.state = 0
            self.date = '-'
            self.user = '-'
            self.return_date = '-'
            return True
        else:
            return False

    def delete_book(self):
        data = Book.load_books_data()
        data['id'] = data['id'].str.strip()
        data = data[data['id'] != str(self.id)]
        data.to_csv("books.csv", index=False)

    @staticmethod
    def add_book(name, author, isbn):
        data = Book.load_books_data()
        data['id'] = data['id'].str.strip()
        new_id = str(data['id'].astype(int).max() + 1)
        new_book = {
            'id': new_id,
            'name': name,
            'author': author,
            'isbn': isbn,
            'state': '0',
            'date': '-',
            'user': '-',
            'return_date': '-'
        }
        data = pandas.concat([data, pandas.DataFrame([new_book])], ignore_index=True)
        data.to_csv("books.csv", index=False)





