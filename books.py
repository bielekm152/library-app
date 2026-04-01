from datetime import datetime
import pandas

class Book():
    def __init__(self, id=None):
        self.id = id
        self.author = None
        self.isbn = None
        self.name = None
        self.state = None
        self.date = None
        self.user = None
        self.return_date = None
        if self.id is not None:
            self.define_book()

    def define_book(self):
        data = pandas.read_csv("books.csv", dtype={'id': str, 'name': str, 'author': str, 'isbn': str, 'state': str, 'date': str, 'user': str, 'return_date': str})

        data['id'] = data['id'].str.strip()

        mask = (data['id'] == str(self.id))
        filtered_data = data[mask]

        if not filtered_data.empty:
            self.name = str(filtered_data['name'].iloc[0])
            self.author = str(filtered_data['author'].iloc[0])
            self.isbn = str(filtered_data['isbn'].iloc[0])
            self.state = str(filtered_data['state'].iloc[0])
            self.date = str(filtered_data['date'].iloc[0])
            self.user = str(filtered_data['user'].iloc[0])
            self.return_date = str(filtered_data['return_date'].iloc[0])
    def borrow_book(self, id):
        if self.state == 'dostupné':
            data = pandas.read_csv("books.csv", dtype={'id': str, 'name': str, 'author': str, 'isbn': str, 'state': str, 'date': str, 'user': str, 'return_date': str})
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 'požičané'
            data.loc[mask, 'date'] = datetime.now().strftime('%d-%m-%Y')
            data.loc[mask, 'user'] = id
            data.loc[mask, 'return_date'] = (datetime.now() + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')   

            data.to_csv("books.csv", index=False)
            self.state = 'požičané'
            self.date = datetime.now().strftime('%d-%m-%Y')
            self.return_date = (datetime.now() + pandas.Timedelta(days=30)).strftime('%d-%m-%Y')
            return True
        elif self.state == 'požičané':
            return False
        
    def return_book(self, user):
        if self.state == 'požičané' and self.user == user:
            data = pandas.read_csv("books.csv", dtype={'id': str, 'name': str, 'author': str, 'isbn': str, 'state': str, 'date': str, 'user': str, 'return_date': str})
            data['id'] = data['id'].str.strip()
            mask = (data['id'] == str(self.id))

            data.loc[mask, 'state'] = 'dostupné'
            data.loc[mask, 'date'] = '-'
            data.loc[mask, 'user'] = '-'
            data.loc[mask, 'return_date'] = '-'

            data.to_csv("books.csv", index=False)
            self.state = 'dostupné'
            self.date = '-'
            self.user = '-'
            self.return_date = '-'
            return True
        elif self.state == 'dostupné':
            return False

    def delete_book(self):
        data = pandas.read_csv("books.csv", dtype={'id': str, 'name': str, 'author': str, 'isbn': str, 'state': str, 'date': str, 'user': str, 'return_date': str})
        data['id'] = data['id'].str.strip()
        data = data[data['id'] != str(self.id)]
        data.to_csv("books.csv", index=False)

    def add_book(self, name, author, isbn):
        data = pandas.read_csv("books.csv", dtype={'id': str, 'name': str, 'author': str, 'isbn': str, 'state': str, 'date': str, 'user': str, 'return_date': str})
        data['id'] = data['id'].str.strip()
        new_id = str(data['id'].astype(int).max() + 1)
        new_book = {
            'id': new_id,
            'name': name,
            'author': author,
            'isbn': isbn,
            'state': 'dostupné',
            'date': '-',
            'user': '-',
            'return_date': '-'
        }
        data = pandas.concat([data, pandas.DataFrame([new_book])], ignore_index=True)
        data.to_csv("books.csv", index=False)





