import flet as ft
import sqlite3
from flet import TextField, ElevatedButton, Text, Row, Column, IconButton, TextButton

#Initialize database and create tables
def initialize():
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    #users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    password TEXT,  officer BOOLEAN DEFAULT 0 )
                   ''')
    #posts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    post_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
    #announcements table
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, announcement TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id))
                   ''')
    conn.commit()
    conn.close()

def insert_user(username, email, password, officer=False):
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    # check if email already exists in the db
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        print("Email already exists!")
        conn.close()
        return

    #add new user in db
    cursor.execute("INSERT INTO users (username, email, password, officer) VALUES (?, ?, ?, ?)",
                   (username, email, password, officer))
    conn.commit()
    conn.close()

#get user's username(un) or email for login
def fetch_user(un_email):
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (un_email, un_email))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_post(user_id, post_text):
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (user_id, post_text) VALUES (?, ?)", (user_id, post_text))
    conn.commit()
    conn.close()

#get all post from all users (fro displaying all post in freedom wall)
def fetch_all_posts():
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT users.username, 
                   posts.post_text, 
                   posts.timestamp, 
                   users.id FROM users JOIN posts ON users.id = posts.user_id ORDER BY posts.timestamp DESC""")
    posts = cursor.fetchall()
    conn.close()
    return [{'username': post[0], 'text': post[1], 'timestamp': post[2], 'user_id': post[3]} for post in posts]

#Add announcement (officer only)
def insert_announcement(user_id, announcement_text):
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("SELECT officer FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    #check if the user is an officer
    if user and user[0] == 1:  
        cursor.execute("INSERT INTO announcements (user_id, announcement) VALUES (?, ?)", 
                       (user_id, announcement_text))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

#fetch announcemnet (for displaying announcemnet)
def fetch_announcements():
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT users.username, announcements.announcement, announcements.timestamp, announcements.id 
                      FROM users 
                      JOIN announcements ON users.id = announcements.user_id 
                      ORDER BY announcements.timestamp DESC""")
    announcements = cursor.fetchall()
    conn.close()
    return [{'username': announcement[0], 'announcement': announcement[1], 'timestamp': announcement[2], 'id': announcement[3]} for announcement in announcements]

#delete announcemnt (officer only)
def delete_announcement(announcement_id):
    conn = sqlite3.connect('clics_portal.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    conn.commit()
    conn.close()
    return True

class SignupPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.username_touched = False
        self.email_touched = False
        self.password_touched = False

    def build(self):
        self.page.clean()
        self.page.title = "Signup"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        #container with the background image
        background = ft.Container(
            content=None,
            width=self.page.width,
            height=self.page.height,
            image_src=r"C:\Users\kathl\Documents\PYTHON\Flet\CSELEC activities\final project - clics\assets\bg.png",
            image_fit=ft.ImageFit.COVER,
        )
        clics_portal= Text(
            value="CLICS PORTAL",
            color="#e1e1d9",
            theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        signup_txt = Text(
            value="Sign Up", 
            color="#e1e1d9", 
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM, 
            weight=ft.FontWeight.BOLD, 
        )
        txt_username = TextField(
            label="Username", 
            content_padding=10,
            color="#e1e1d9", 
            border_color="#3b4c54",     
            label_style=ft.TextStyle(color="#a49898"),
        )
        txt_email = TextField(
            label="Email", 
            content_padding=10,
            color="#e1e1d9", 
            border_color="#3b4c54",     
            label_style=ft.TextStyle(color="#a49898"),
        )
        txt_password = TextField(
            label="Password", 
            content_padding=10,
            password=True, 
            color="#e1e1d9", 
            border_color="#3b4c54", 
            label_style=ft.TextStyle(color="#a49898")
        )
        user_type = ft.Dropdown(
            label="User Type",
            options=[
                ft.dropdown.Option("Officer"), 
                ft.dropdown.Option("Member")   
            ],
            border_color="#3b4c54",
            label_style=ft.TextStyle(color="#a49898"),
            color="#e1e1d9",
            fill_color="#00000",
            bgcolor="#3b4c54",
        )
        
        #error messages (initially empty)
        error_username = Text(value="", color="#c30101", visible=False)
        error_email = Text(value="", color="#c30101", visible=False)
        error_password = Text(value="", color="#c30101", visible=False)

        signup_btn = ElevatedButton(
            text='Sign Up', 
            width=120, 
            disabled=True,
            color="#0f212b", 
            bgcolor="#e1e1d9", 
            opacity=0.5
        )
        login_btn = TextButton(text="Already have an account?", width=90, on_click=lambda _: LoginPage(self.page).build())

        def validate_input(e):
            #check if all fields have values and if length is greater than 5 char
            valid_username = len(txt_username.value) >= 5
            valid_email = len(txt_email.value) >= 5
            valid_password = len(txt_password.value) >= 5
            signup_btn.disabled = not all([valid_username, valid_email, valid_password, user_type.value])

            if not signup_btn.disabled:
                signup_btn.opacity = 1
            else:
                signup_btn.opacity = 0.5

            #update error visibility based on input length when the field loses focus
            if self.username_touched:
                error_username.visible = not valid_username
                error_username.value = "Username must be at least 5 characters."
            if self.email_touched:
                error_email.visible = not valid_email
                error_email.value = "Email must be at least 5 characters."
            if self.password_touched:
                error_password.visible = not valid_password
                error_password.value = "Password must be at least 5 characters."

            self.page.update()

        #add user to db after signup
        def sign_up(e):
            officer = user_type.value == "Officer"
            insert_user(
                txt_username.value,
                txt_email.value,
                txt_password.value,
                officer
            )
            LoginPage(self.page).build()

        #add validation to all inputs
        txt_username.on_change = validate_input
        txt_email.on_change = validate_input
        txt_password.on_change = validate_input
        user_type.on_change = validate_input
        signup_btn.on_click = sign_up

        #track user interaction and validate only after user exits the field or move to other field
        def on_blur_username(e):
            self.username_touched = True
            validate_input(e)
        def on_blur_email(e):
            self.email_touched = True
            validate_input(e)
        def on_blur_password(e):
            self.password_touched = True
            validate_input(e)

        #set on_blur event listeners to track if user exits the field
        txt_username.on_blur = on_blur_username
        txt_email.on_blur = on_blur_email
        txt_password.on_blur = on_blur_password

        signup= ft.Container(
            content=ft.ResponsiveRow(
                [
                    clics_portal,
                    ft.Container(height=60),
                    signup_txt,
                    txt_username,
                    error_username,
                    txt_email,
                    error_email,
                    txt_password,
                    error_password,
                    user_type,
                    ft.Container(height=30),
                    Row([signup_btn], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=80),
                    login_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20, 
            margin=20,
            alignment=ft.alignment.center,
        )
        self.page.add(
            ft.Stack(
                [background, signup]
            )
        )

class LoginPage:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self):
        self.page.clean()
        self.page.title = "Login"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        #container with the background image
        background = ft.Container(
            content=None,
            width=self.page.width,
            height=self.page.height,
            image_src=r"C:\Users\kathl\Documents\PYTHON\Flet\CSELEC activities\final project - clics\assets\bg.png",
            image_fit=ft.ImageFit.COVER,
        )

        clics_portal = Text(
            value="CLICS PORTAL",
            color="#e1e1d9",
            theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        login_txt = Text(
            value="Login",
            color="#e1e1d9",
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            weight=ft.FontWeight.BOLD,
        )
        username_email = TextField(
            label="Username or Email", 
            content_padding=10,
            color="#e1e1d9", 
            border_color="#3b4c54",     
            label_style=ft.TextStyle(color="#a49898"),
        )
        password = TextField(
            label="Password", 
            content_padding=10,
            password=True, 
            color="#e1e1d9", 
            border_color="#3b4c54", 
            label_style=ft.TextStyle(color="#a49898")
        )
        user_type = ft.Dropdown(
            label="User Type",
            options=[
                ft.dropdown.Option("Officer"),
                ft.dropdown.Option("Member")
            ],
            border_color="#3b4c54",
            label_style=ft.TextStyle(color="#a49898"),
            color="#e1e1d9",
            fill_color="#00000",
            bgcolor="#3b4c54"
        )
        
        login_btn = ElevatedButton(
            text="Login", 
            width=120, 
            color="#161616", 
            bgcolor="#e1e1d9"
            
        )
        signup_btn = TextButton(
            text="Sign Up",  
            on_click=lambda _: SignupPage(self.page).build()
        )
        error_message = Text(value="", color="red", visible=False)

        def login(e):
            user_data = fetch_user(username_email.value)
            if user_data and user_data[3] == password.value:
                officer = user_data[4] == 1
                if (officer and user_type.value == "Officer") or (not officer and user_type.value == "Member"):
                    #Proceed to free wall
                    WallPage(self.page, {'id': user_data[0], 'username': user_data[1], 'email': user_data[2], 'officer': officer}).build()
                else:
                    error_message.value = "User type mismatch! Select the correct user type."
                    error_message.visible = True
            else:
                error_message.value = "Invalid login details! Please try again."
                error_message.visible = True

            self.page.update()
        login_btn.on_click = login

        #overlay the login container on top of the bg image
        login_cont= ft.Container(
            content=ft.ResponsiveRow(
                [
                    clics_portal,
                    ft.Container(height=60),
                    login_txt,
                    username_email,
                    password,
                    user_type,
                    ft.Container(height=30),
                    Row([login_btn], alignment=ft.MainAxisAlignment.CENTER),
                    error_message, 
                    ft.Container(height=120),
                    Row([Text("Don't have an account?",color ="#E9E9E7"), signup_btn],alignment=ft.MainAxisAlignment.CENTER, )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            margin=ft.Margin(top=50, right=10, bottom=20, left=10), 
            alignment=ft.alignment.center,
        )

        #Add the background and the login container to the page
        self.page.add(
            ft.Stack(
                [background, login_cont]
            )
        )

class WallPage:
    def __init__(self, page: ft.Page, user_data):
        self.page = page
        self.user_data = user_data

    def build(self):
        self.page.clean()
        self.page.title = "Freedom Wall"
        self.page.bgcolor = "#161616"
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        def add_post(e):
            if post_field.value:
                insert_post(self.user_data['id'], post_field.value)
                post_field.value = ""
                self.build()

        post_field = TextField(label="What's new?", focused_color="#161616",color="#161616", label_style=ft.TextStyle(color="#0f212b"), width=250, bgcolor="#e1e1d9", multiline=True)
        post_btn = IconButton(icon=ft.icons.POST_ADD, on_click=add_post, icon_color="#e1e1d9")
        posts = fetch_all_posts()

        #post display area
        post_view = ft.ListView([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.IconButton(icon=ft.icons.PERSON_2_ROUNDED, padding=0, width=20,
                                      icon_size=18, icon_color="#3b4c54", bgcolor="#e1e1d9"),
                        ft.Text(f"{post['username']}", weight="bold", color="#e1e1d9"),
                    ]),
                    ft.Text(post['text'], color="#a49898"),
                ]),
                bgcolor="#1c4e6e",
                border_radius=10,
                padding=10,
                width=350,
            ) for post in posts ],
            spacing=20,
            expand=True
        )
        navbar = ft.Row(
            [
                ft.IconButton(icon=ft.icons.HOME, icon_size=24,icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: self.build(),
                ),
                ft.IconButton(icon=ft.icons.ANNOUNCEMENT_OUTLINED, icon_size=24, icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: AnnouncementPage(self.page, self.user_data).build(),
                ),
                ft.IconButton( icon=ft.icons.LOGOUT_SHARP, icon_size=24, icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: LoginPage(self.page).build(),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50,  
        )
        #add all components to the page
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        navbar,
                        ft.Row(
                            [post_field, post_btn], 
                            alignment=ft.MainAxisAlignment.END
                        ),
                        ft.Text("Freedom Wall", weight="bold", color="#e1e1d9",theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                        post_view,
                    ],
                ),
                margin=10,
                padding=10,
                height=self.page.height,
            ),
             
        )

class AnnouncementPage:
    def __init__(self, page: ft.Page, user_data):
        self.page = page
        self.user_data = user_data

    def build(self):
        self.page.clean()
        self.page.title = "Announcements"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.bgcolor = "#161616"

        def add_announcement(e):
            if announcement_field.value:
                if insert_announcement(self.user_data['id'], announcement_field.value):
                    announcement_field.value = ""
                    self.build()

        def remove_announcement(announcement_id):
            if self.user_data.get('officer', False):
                if delete_announcement(announcement_id):
                    self.build()  #refresh the page

        #adding announcement for officer only
        announcement_controls = []
        if self.user_data.get('officer', False):
            announcement_field = TextField(label="Add Announcement", width=250, label_style=ft.TextStyle(color="#0f212b"), color="#161616", bgcolor="#e1e1d9", multiline=True)
            announcement_btn = IconButton(icon=ft.icons.ANNOUNCEMENT_SHARP, icon_color= "#e1e1d9",on_click=add_announcement)
            announcement_controls = [Row([announcement_field, announcement_btn], alignment=ft.MainAxisAlignment.END)]

        announcements = fetch_announcements()

        txt_ann = ft.Text("Announcements", weight="bold", color="#e1e1d9", theme_style=ft.TextThemeStyle.HEADLINE_SMALL)
        #display announcment
        announcement_view = ft.ListView([
            ft.Container(
                content=Row([
                    Column([
                        Row([
                            ft.IconButton(icon=ft.icons.PERSON_2_SHARP, padding=0, width=20, icon_size=18, 
                                        icon_color="#43545c", bgcolor="#efece5"),
                            ft.Text(f"{a['username']}", weight="bold", color="#efece5"),
                        ]),
                        ft.Text(a['announcement'], color="#E9E9E7" ),
                    ], spacing=5, expand=True),
                    IconButton( icon=ft.icons.DELETE_FOREVER_SHARP, icon_color="#d0bdb6",
                        on_click=lambda e, aid=a['id']: remove_announcement(aid), visible=self.user_data.get('officer', False),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#3b4c54",
                padding=10,
                margin=5,
                width=350,
            ) for a in announcements],
            spacing=20,
            expand=True
        )

        navbar = ft.Row(
            [
                ft.IconButton( icon=ft.icons.HOME, icon_size=24, icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: WallPage(self.page, self.user_data).build(),
                ),
                ft.IconButton(icon=ft.icons.ANNOUNCEMENT_OUTLINED, icon_size=24,icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: self.build(),
                ),
                ft.IconButton( icon=ft.icons.LOGOUT_SHARP, icon_size=24, icon_color="#e1e1d9",
                              bgcolor="transparent", on_click=lambda _: LoginPage(self.page).build(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50,
        )
        #For officers
        if announcement_controls:  
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        navbar,
                        announcement_controls[0],
                        txt_ann,
                        announcement_view,
                    ]),
                    margin=10,
                    padding=15,
                    height=self.page.height,
                )
            )
        #for members
        else:
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        navbar,
                        txt_ann,
                        announcement_view,
                    ]),
                    margin=10,
                    padding=15,
                    height=self.page.height,
                )
            )

def main(page: ft.Page):  
    page.window_height = 720
    page.window_width = 360
    page.padding=0
    initialize()

    LoginPage(page).build()

ft.app(target=main)
