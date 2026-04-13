import pandas

class User:
    def __init__(self):
        self.u_id = None
        self.email = None
        self.password = None
        self.name = None
        self.role = None

    def authenticate(self, username, password):
        data = pandas.read_csv("logins.csv", dtype={'email': str, 'password': str}) # Definujte typ stlpcov pri nacitani

        # Odstráňte medzery z emailu a hesla v DataFrame
        data['email'] = data['email'].str.strip()
        data['password'] = data['password'].str.strip()

        username = str(username).strip()  # Odstráňte medzery z inputu
        password = str(password).strip()  # Odstráňte medzery z inputu

        mask = (data['email'] == username) & (data['password'] == password)
        filtered_data = data[mask]

        if not filtered_data.empty:
            self.u_id = str(filtered_data['id'].iloc[0])
            self.email = str(filtered_data['email'].iloc[0])
            self.password = str(filtered_data['password'].iloc[0])
            self.name = str(filtered_data['name'].iloc[0])
            self.role = str(filtered_data['role'].iloc[0])
            return True
        else:
            self.u_id = None
            self.email = None
            self.password = None
            self.name = None
            self.role = None
            return False

    def create_user(self, email, password, name, role):
        data = pandas.read_csv("logins.csv", dtype={'id': str, 'email': str, 'password': str, 'name': str, 'role': str})

        email = str(email).strip()
        password = str(password).strip()
        name = str(name).strip()
        role = str(role).strip().lower()

        if not email or not password or not name:
            return False, "Vypln vsetky polia"

        data['id'] = data['id'].astype(str).str.strip()
        data['email'] = data['email'].astype(str).str.strip()

        if email in data['email'].values:
            return False, "Pouzivatel s tymto e-mailom uz existuje"

        new_id = str(data['id'].astype(int).max() + 1)
        new_user = pandas.DataFrame([
            {
                'id': new_id,
                'email': email,
                'password': password,
                'name': name,
                'role': role
            }
        ])
        data = pandas.concat([data, new_user], ignore_index=True)
        data.to_csv("logins.csv", index=False)
        return True, "Registracia bola uspesna"