from tkinter import *
from tkinter import ttk, messagebox
from customtkinter import *
from PIL import Image, ImageTk
import customtkinter
import datetime
import os

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

main_color = '#62e2ff'
hover_color = '#74f0ff'

currentTime = datetime.datetime.now()
currentDate = str(currentTime.year) + '-' + str(currentTime.month) + '-' + str(currentTime.day)
currentClock = str(currentTime.hour) + ':' + str(currentTime.minute) + ':' + str(currentTime.second)

# Dữ liệu mẫu thay cho database
SAMPLE_BOOKS = [
    {'id': 1, 'name': 'Python 101', 'author': 'John Doe', 'publisher': 'TechBooks', 'types': 'Programming', 'quantity': 5, 'storage': 'A1', 'content': 'Intro to Python', 'borrowed': False},
    {'id': 2, 'name': 'AI Basics', 'author': 'Jane Smith', 'publisher': 'AI Press', 'types': 'AI', 'quantity': 2, 'storage': 'B2', 'content': 'Artificial Intelligence', 'borrowed': True},
]
SAMPLE_MEMBERS = [
    {'id': '123456789012', 'full_name': 'Nguyen Van A', 'gender': 'male', 'birthday': '2000-01-01', 'address': 'Hanoi'},
    {'id': '987654321098', 'full_name': 'Tran Thi B', 'gender': 'female', 'birthday': '1999-12-31', 'address': 'HCM'},
]

class BackgroundImageAutoFitContent(CTkFrame):
    def __init__(self, master, *pargs):
        CTkFrame.__init__(self, master, *pargs)
        # Không dùng ảnh nền nữa, chỉ để khung trống hoặc màu nền mặc định
        self.background = Label(self)
        self.background.pack(fill=BOTH, expand=YES)

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title('Gobrary Library Management Application')
        self.width = int(self.winfo_screenwidth() / 2) - int(1280 / 2)
        self.height = int(self.winfo_screenheight() / 2) - int(720 / 2)
        self.minsize(width=1280, height=720)
        self.geometry(f'1280x720+{self.width}+{self.height}')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ####

        ############ # App #############

        ####

        self.navigationFrame = CTkFrame(self)
        self.navigationFrame.grid(row=0, column=0, sticky="nsew")
        self.navigationFrame.grid_rowconfigure(4, weight=1)

        self.navigationFrameLabel = CTkLabel(
            self.navigationFrame, text='  Gobrary', font=CTkFont('Arial', size=20, weight='bold')
        )
        self.navigationFrameLabel.grid(row=0, column=0, padx=20, pady=20)

        self.homeButton = CTkButton(
            self.navigationFrame, height=50, text="Home",
            fg_color='transparent',
            text_color=('black', 'white'), hover_color=('gray75', 'gray25'),
            font=CTkFont('Arial', size=14, weight='normal'), anchor='w',
            command=self.HomeButtonEvent
        )
        self.homeButton.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="ew")

        self.bookButton = CTkButton(
            self.navigationFrame, height=50, text="Book",
            fg_color='transparent',
            text_color=('black', 'white'), hover_color=('gray75', 'gray25'),
            anchor='w', font=CTkFont('Arial', size=14, weight='normal'),
            command=self.BookButtonEvent
        )
        self.bookButton.grid(row=2, column=0, padx=5, pady=(5, 0), sticky="ew")

        self.userButton = CTkButton(
            self.navigationFrame, height=50, text="Account",
            fg_color='transparent',
            text_color=('black', 'white'), hover_color=('gray75', 'gray25'),
            anchor='w', font=CTkFont('Arial', size=14, weight='normal'),
            command=self.UserButtonEvent
        )
        self.userButton.grid(row=3, column=0, padx=5, pady=(5, 0), sticky="ew")

        self.appearanceModeMenu = CTkOptionMenu(
            self.navigationFrame, values=['System', 'Light', 'Dark'],
            command=self.ChangeAppearanceModeEvent
        )
        self.appearanceModeMenu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        ####

        self.contentFrame = CTkFrame(self, fg_color=('#AAAAAA', '#555555'))
        self.contentFrame.grid(row=0, column=1, sticky="nsew")
        self.contentFrame.grid_rowconfigure(0, weight=1)
        self.contentFrame.grid_columnconfigure(1, weight=1)

        ####

        self.homeFrame = CTkFrame(self.contentFrame, fg_color='transparent')
        self.homeFrame.grid_columnconfigure(0, weight=1)
        self.homeFrame.grid_rowconfigure(0, weight=0)
        self.homeFrame.grid_rowconfigure(1, weight=1)
        self.homeFrame.grid_rowconfigure(2, weight=0)
        self.bookFrame = CTkFrame(self.contentFrame, fg_color='transparent')
        self.bookFrame.grid_columnconfigure(0, weight=1)
        self.bookFrame.grid_columnconfigure(1, weight=0)
        self.bookFrame.grid_rowconfigure(0, weight=0)
        self.bookFrame.grid_rowconfigure(1, weight=1)
        self.bookFrame.grid_rowconfigure(2, weight=0)
        self.userFrame = CTkFrame(self.contentFrame, fg_color='transparent')
        self.userFrame.grid_columnconfigure(0, weight=1)

        #### # Home

        self.homeTopFrame = CTkFrame(self.homeFrame, fg_color='transparent')
        self.homeTopFrame.grid(row=0, column=0, sticky='nsew')
        self.homeTopFrame.grid_columnconfigure(0, weight=1)
        self.homeTopFrame.grid_rowconfigure(0, weight=1)

        self.homeCenterFrame = CTkFrame(self.homeFrame, fg_color='transparent')  # ('#555555', '#AAAAAA')
        self.homeCenterFrame.grid(row=1, column=0, padx=5, sticky='nsew')
        self.homeCenterFrame.grid_columnconfigure(0, weight=1)
        self.homeCenterFrame.grid_rowconfigure(0, weight=1)

        self.homeBottomFrame = CTkFrame(self.homeFrame, fg_color='transparent')
        self.homeBottomFrame.grid(row=2, column=0, sticky='nsew')
        self.homeBottomFrame.columnconfigure(0, weight=1)

        ##

        self.homeBackgroundImageFrame = CTkFrame(self.homeCenterFrame)
        self.homeBackgroundImageFrame.grid(row=0, column=0, sticky='nsew')
        # BackgroundImageAutoFitContent.path = './icons/candy.png'
        self.homeBackgroundImageLabel = BackgroundImageAutoFitContent(self.homeBackgroundImageFrame)
        self.homeBackgroundImageLabel.pack(fill=BOTH, expand=YES)

        ##

        self.homeWelcomeFrame = CTkFrame(self.homeCenterFrame, bg_color='transparent')
        self.homeWelcomeFrame.grid(row=0, column=0, sticky='new')
        self.homeWelcomeFrame.grid_columnconfigure(0, weight=1)
        self.homeWelcomeLabel = CTkLabel(
            self.homeWelcomeFrame, text='Welcome to Gobrary',
            bg_color='transparent', text_color=('black', 'white'),
            font=CTkFont('Arial', size=32, weight='bold')
        )
        self.homeWelcomeLabel.grid(row=0, column=0, pady=20, sticky='nsew')

        self.homeCopyrightFrame = CTkFrame(self.homeCenterFrame, bg_color='transparent')
        self.homeCopyrightFrame.grid(row=0, column=0, sticky='sew')
        self.homeCopyrightFrame.grid_columnconfigure(0, weight=1)
        self.homeCopyrightLabel = CTkLabel(
            self.homeCopyrightFrame,
            text='Powered by Gorth Inc. Copyright © 2020 - 2024 Gorth Inc. All rights reserved.',
            bg_color='transparent', text_color=('black', 'white'),
            font=CTkFont('Arial', size=20, weight='normal')
        )
        self.homeCopyrightLabel.grid(row=0, column=0, pady=20, sticky='nsew')

        # self.homeMemberFrame = CTkFrame(self.homeCenterFrame, bg_color='transparent')
        # self.homeMemberFrame.grid(row=0, column=0, padx=20, sticky='ew')
        # self.homeMemberFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        # self.homeMemberLabel1 = CTkLabel(
        #     self.homeMemberFrame, text='Japtor\nLeader\nJiangFam',
        #     font=CTkFont('Arial', size=20, weight='bold')
        # )
        # self.homeMemberLabel1.grid(row=0, column=0, padx=10, sticky='nsew')
        # self.homeMemberLabel2 = CTkLabel(
        #     self.homeMemberFrame
        # )
        # self.homeMemberLabel2.grid(row=0, column=1, padx=10, sticky='nsew')
        # self.homeMemberLabel3 = CTkLabel(
        #     self.homeMemberFrame
        # )
        # self.homeMemberLabel3.grid(row=0, column=2, padx=10, sticky='nsew')
        # self.homeMemberLabel4 = CTkLabel(
        #     self.homeMemberFrame
        # )
        # self.homeMemberLabel4.grid(row=0, column=3, padx=10, sticky='nsew')

        ##

        self.buttonLibrary = CTkButton(
            self.homeTopFrame, text='Gorth Inc.',  # Library
            width=150, height=50, fg_color='black', hover_color='white',
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold')
        )
        self.buttonLibrary.pack(side='left', padx=(5, 0), pady=5)

        self.buttonHomeAccount = CTkButton(
            self.homeTopFrame, text='Account',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.UserButtonEvent
        )
        self.buttonHomeAccount.pack(side='right', padx=(0, 5), pady=5)

        self.buttonNothing = CTkButton(
            self.homeBottomFrame, text='Nothing :)',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'), state='disabled'
        )
        self.buttonNothing.pack(side='right', padx=(0, 5), pady=5)

        self.buttonJaptor = CTkButton(
            self.homeBottomFrame, text='Founder\nGiang', fg_color='#FF00AA', hover_color='black',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold')
        )
        self.buttonJaptor.pack(side='left', padx=(5, 0), pady=5)

        self.buttonPayHD = CTkButton(
            self.homeBottomFrame, text='Helper\nPhan Anh', fg_color='#00BFFF', hover_color='black',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold')
        )
        self.buttonPayHD.pack(side='left', padx=(5, 0), pady=5)

        self.buttonSkydrive = CTkButton(
            self.homeBottomFrame, text='Designer\nQuốc Hội', fg_color='#7652D8', hover_color='black',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold')
        )
        self.buttonSkydrive.pack(side='left', padx=(5, 0), pady=5)

        self.buttonHieunu = CTkButton(
            self.homeBottomFrame, text='Editor\nHiếu', fg_color='#76989B', hover_color='black',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold')
        )
        self.buttonHieunu.pack(side='left', padx=(5, 0), pady=5)

        #### # Book

        self.bookTopFrame = CTkFrame(self.bookFrame, fg_color='transparent')
        self.bookTopFrame.grid(row=0, column=0, sticky='nsew')
        self.bookTopFrame.grid_columnconfigure(0, weight=1)
        self.bookTopFrame.grid_rowconfigure(0, weight=1)

        self.bookMainFrame = CTkFrame(self.bookFrame, fg_color=('#555555', '#AAAAAA'))  # 'transparent'
        self.bookMainFrame.grid(row=1, column=0, padx=5, sticky='nsew')
        self.bookMainFrame.grid_rowconfigure(0, weight=1)
        self.bookMainFrame.grid_columnconfigure(0, weight=1)

        self.bookCenterFrame = CTkFrame(self.bookMainFrame, fg_color='transparent')
        self.bookCenterFrame.grid(row=0, column=0)  # , sticky='nsew'
        self.bookCenterFrame.grid_columnconfigure(0, weight=6)
        self.bookCenterFrame.grid_columnconfigure(1, weight=4)
        self.bookCenterFrame.grid_rowconfigure(0, weight=1)

        self.bookCenterLeftFrame = CTkFrame(self.bookCenterFrame, fg_color=('#555555', '#AAAAAA'))
        self.bookCenterLeftFrame.grid(row=0, column=0, sticky='nsew')  # , padx=(0, 5)
        self.bookCenterLeftFrame.grid_columnconfigure(0, weight=1)
        self.bookCenterLeftFrame.grid_rowconfigure(0, weight=1)

        self.bookCenterRightFrame = CTkFrame(self.bookCenterFrame, fg_color=('#555555', '#AAAAAA'))
        self.bookCenterRightFrame.grid(row=0, column=1, sticky='nsew')
        self.bookCenterRightFrame.grid_columnconfigure(0, weight=1)
        self.bookCenterRightFrame.grid_rowconfigure((0, 1), weight=1)
        self.bookCenterRightTopFrame = CTkFrame(self.bookCenterRightFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.bookCenterRightTopFrame.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='nsew')
        self.bookCenterRightTopFrame.grid_columnconfigure(0, weight=1)
        self.bookCenterRightTopFrame.grid_rowconfigure(0, weight=1)
        self.bookCenterRightBottomFrame = CTkFrame(self.bookCenterRightFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.bookCenterRightBottomFrame.grid(row=1, column=0, padx=(0, 5), pady=(0, 5), sticky='nsew')
        self.bookCenterRightBottomFrame.grid_columnconfigure(0, weight=1)
        self.bookCenterRightBottomFrame.grid_rowconfigure(0, weight=1)

        self.bookBottomFrame = CTkFrame(self.bookFrame, fg_color='transparent')
        self.bookBottomFrame.grid(row=2, column=0, sticky='nsew')
        self.bookBottomFrame.grid_columnconfigure(0, weight=1)

        ##

        self.buttonHomeBook = CTkButton(
            self.bookTopFrame, text='Home List',
            width=150, height=50, compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            state='disabled', command=self.HomeListEvent
        )
        self.buttonHomeBook.pack(side='left', padx=(5, 0), pady=5)
        self.buttonHomeBook.pack_forget()

        self.buttonAddBook = CTkButton(
            self.bookTopFrame, text='Add Book',
            width=150, height=50, compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.AddBookEvent
        )
        self.buttonAddBook.pack(side='left', padx=(5, 0), pady=5)
        self.buttonAddBook.pack_forget()

        self.buttonDelBook = CTkButton(
            self.bookTopFrame, text='Del Book',
            width=150, height=50, compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.DelBookEvent
        )
        self.buttonDelBook.pack(side='left', padx=(5, 0), pady=5)
        self.buttonDelBook.pack_forget()

        self.buttonBorBook = CTkButton(
            self.bookTopFrame, text='Borrow',
            width=150, height=50, compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.BorBookEvent
        )
        self.buttonBorBook.pack(side='left', padx=(5, 0), pady=5)
        self.buttonBorBook.pack_forget()

        self.buttonRtnBook = CTkButton(
            self.bookTopFrame, text='Return',
            width=150, height=50, compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.RtnBookEvent
        )
        self.buttonRtnBook.pack(side='left', padx=(5, 0), pady=5)
        self.buttonRtnBook.pack_forget()

        ##

        self.buttonBookAccount = CTkButton(
            self.bookTopFrame, text='Account',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.UserButtonEvent
        )
        self.buttonBookAccount.pack(side='right', padx=(0, 5), pady=5)

        self.buttonGiveBook = CTkButton(
            self.bookBottomFrame, text='Nothing :)',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            state='disabled'
        )
        self.buttonGiveBook.pack(side='right', padx=(0, 5), pady=5)

        ##

        self.tabs = CTkTabview(self.bookCenterLeftFrame)
        self.tabs.grid(padx=5, pady=(0, 5), sticky='nsew')
        # self.tabs.grid_columnconfigure(0, weight=1)
        self.tab1 = self.tabs.add('Library Management')
        self.tab1.columnconfigure(0, weight=6)
        self.tab1.columnconfigure(1, weight=4)
        self.tab1.rowconfigure(0, weight=1)
        # self.tab2 = self.tabs.add('Statistics')

        ##

        # Thay CTkListbox bằng CTkTextbox để hiển thị danh sách
        self.listBooks = CTkTextbox(self.tab1, font=CTkFont(family='Arial', size=14, weight='bold'), width=200, height=200)
        self.listBooks.grid(row=0, column=0, padx=(10, 0), pady=(0, 10), sticky='nsew')
        self.listDetails = CTkTextbox(self.tab1, font=CTkFont('Arial', size=14, weight='bold'), width=200, height=200)
        self.listDetails.grid(row=0, column=1, padx=(10, 10), pady=(0, 10), sticky='nsew')
        ##
        # self.labelBookCount = CTkLabel(self.tab2, text='', font=CTkFont('Arial', size=20, weight='bold'))
        # self.labelBookCount.grid(row=0, padx=50, pady=(50, 20), sticky='w')
        # self.labelMemberCount = CTkLabel(self.tab2, text='a', font=CTkFont('Arial', size=20, weight='bold'))
        # self.labelMemberCount.grid(row=1, padx=50, pady=20, sticky='w')
        # self.labelTakenCount = CTkLabel(self.tab2, text='a', font=CTkFont('Arial', size=20, weight='bold'))
        # self.labelTakenCount.grid(row=2, padx=50, pady=20, sticky='w')

        ##

        self.searchBar = CTkFrame(self.bookCenterRightTopFrame)  # , text='Search Box'
        # self.searchBar.pack(side='left', padx=10, pady=20, anchor='nw')
        self.searchBar.grid(row=0, column=0, sticky='ns')  # padx=10, pady=20,
        self.searchBar.grid_columnconfigure(0, weight=1)
        self.searchBar.grid_rowconfigure((0, 3), weight=1)
        self.searchBar0 = CTkLabel(
            self.searchBar, text='Search Box',
            fg_color='transparent', text_color=('black', 'white'),
            font=CTkFont('Arial', size=24, weight='bold')
        )
        self.searchBar0.grid(row=0, column=0, pady=30, sticky='n')
        self.searchBar1 = CTkFrame(self.searchBar, fg_color='transparent')
        self.searchBar1.grid(row=1, column=0, pady=15, sticky='s')
        self.searchBar2 = CTkFrame(self.searchBar, fg_color='transparent')
        self.searchBar2.grid(row=2, column=0, pady=15, sticky='n')
        self.searchBar3 = CTkFrame(self.searchBar, fg_color='transparent')
        self.searchBar3.grid(row=3, column=0, pady=15, sticky='s')
        self.labelSearch = CTkLabel(
            self.searchBar1, text='Search: ', text_color=('black', 'white'),
            font=CTkFont('Arial', size=18, weight='bold')
        )
        self.labelSearch.grid(row=1)
        self.entrySearch = CTkEntry(self.searchBar2, font=CTkFont('Arial', size=16, weight='bold'), width=320)
        self.entrySearch.grid(row=2)
        self.buttonSearch = CTkButton(
            self.searchBar3, text='Search', width=160,
            font=CTkFont('Arial', size=16, weight='bold'),
            command=self.SearchBook
        )
        self.buttonSearch.grid(row=3)

        self.listBar = CTkFrame(self.bookCenterRightBottomFrame)  # , fg_color='transparent'
        # self.listBar.pack(side='left', padx=10, pady=20, anchor='nw')
        self.listBar.grid(row=0, column=0, sticky='ns')  # , padx=10, pady=20
        self.listBar.grid_columnconfigure(0, weight=1)
        self.listBar.grid_rowconfigure((0, 2), weight=1)
        self.listBar0 = CTkLabel(
            self.listBar, text='List Box',
            fg_color='transparent', text_color=('black', 'white'),
            font=CTkFont('Arial', size=24, weight='bold')
        )
        self.listBar0.grid(row=0, column=0, pady=30, sticky='n')
        self.listBar1 = CTkFrame(self.listBar, fg_color='transparent')
        self.listBar1.grid(row=1, column=0, pady=15, sticky='s')
        self.listBar2 = CTkFrame(self.listBar, fg_color='transparent')
        self.listBar2.grid(row=2, column=0, pady=15, sticky='n')
        self.listBar3 = CTkFrame(self.listBar, fg_color='transparent')
        self.listBar3.grid(row=3, column=0, pady=15, sticky='s')
        self.labelList = CTkLabel(
            self.listBar1, text='Sort by:', text_color=('black', 'white'),
            font=CTkFont('Arial', size=18, weight='bold')
        )
        self.labelList.grid(row=1)
        self.listChoice = IntVar()
        ##
        self.radioButton1 = CTkRadioButton(
            self.listBar2, text='All Books',
            variable=self.listChoice, value=1,
            font=CTkFont('Arial', size=12, weight='bold')
        )
        self.radioButton2 = CTkRadioButton(
            self.listBar2, text='In Library',
            variable=self.listChoice, value=2,
            font=CTkFont('Arial', size=12, weight='bold')
        )
        self.radioButton3 = CTkRadioButton(
            self.listBar2, text='Borrowed Books',
            variable=self.listChoice, value=3,
            font=CTkFont('Arial', size=12, weight='bold')
        )
        self.radioButton1.grid(row=0, column=0)
        self.radioButton2.grid(row=0, column=1)
        self.radioButton3.grid(row=0, column=2)
        self.buttonList = CTkButton(
            self.listBar3, text='List Books', width=160,
            font=CTkFont('Arial', size=16, weight='bold'),
            command=self.ListBook
        )
        self.buttonList.grid(row=3, column=0)

        self.bookCenterFrame.grid_forget()

        ############ # Form ############

        #### # BorBook Form

        self.borFrame = CTkFrame(self.bookMainFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.borFrame.grid(row=0, column=0, sticky='nsew')
        self.borFrame.grid_columnconfigure(0, weight=1)
        self.borFrame.grid_rowconfigure(8, weight=1)
        self.borLabel = CTkLabel(
            self.borFrame, text="Borrow Book",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.borLabel.grid(row=0, column=0, padx=30, pady=30)
        self.borNameEntry = CTkEntry(
            self.borFrame, width=320, placeholder_text="name book",
            font=CTkFont(family='Arial', size=14)
        )
        self.borNameEntry.grid(row=1, column=0, padx=30, pady=(15, 15))
        # self.borStoragedEntry = CTkEntry(self.borFrame, width=320, placeholder_text="storaged", font=CTkFont(family='Arial', size=14))
        # self.borStoragedEntry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.borFormButton = CTkButton(self.borFrame, text="Borrow", width=160, command=self.BorBook)
        self.borFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.borFrame.grid_forget()

        #### # RtnBook Form

        self.rtnFrame = CTkFrame(self.bookMainFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.rtnFrame.grid(row=0, column=0, sticky='nsew')
        self.rtnFrame.grid_columnconfigure(0, weight=1)
        self.rtnFrame.grid_rowconfigure(8, weight=1)
        self.rtnLabel = CTkLabel(
            self.rtnFrame, text="Return Book",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.rtnLabel.grid(row=0, column=0, padx=30, pady=30)
        self.rtnNameEntry = CTkEntry(
            self.rtnFrame, width=320, placeholder_text="name book",
            font=CTkFont(family='Arial', size=14)
        )
        self.rtnNameEntry.grid(row=1, column=0, padx=30, pady=(15, 15))
        # self.rtnNameEntry = CTkEntry(self.rtnFrame, width=320, placeholder_text="id person", font=CTkFont(family='Arial', size=14))
        # self.rtnNameEntry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.rtnFormButton = CTkButton(self.rtnFrame, text="Return", width=160, command=self.RtnBook)
        self.rtnFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.rtnFrame.grid_forget()

        #### # AddBook Form

        self.addFrame = CTkFrame(self.bookMainFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.addFrame.grid(row=0, column=0, sticky='nsew')
        self.addFrame.grid_columnconfigure(0, weight=1)
        self.addFrame.grid_rowconfigure(8, weight=1)
        self.addLabel = CTkLabel(
            self.addFrame, text="Add Book",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.addLabel.grid(row=0, column=0, padx=30, pady=30)
        self.addNameEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="name book",
            font=CTkFont(family='Arial', size=14)
        )
        self.addNameEntry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.addAuthorEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="author",
            font=CTkFont(family='Arial', size=14)
        )
        self.addAuthorEntry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.addPublisherEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="publisher",
            font=CTkFont(family='Arial', size=14)
        )
        self.addPublisherEntry.grid(row=3, column=0, padx=30, pady=(0, 15))
        self.addTypesEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="types",
            font=CTkFont(family='Arial', size=14)
        )
        self.addTypesEntry.grid(row=4, column=0, padx=30, pady=(0, 15))
        self.addQuantityEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="quantity",
            font=CTkFont(family='Arial', size=14)
        )
        self.addQuantityEntry.grid(row=5, column=0, padx=30, pady=(0, 15))
        self.addContentEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="content",
            font=CTkFont(family='Arial', size=14)
        )
        self.addContentEntry.grid(row=6, column=0, padx=30, pady=(0, 15))
        self.addStoragedEntry = CTkEntry(
            self.addFrame, width=320, placeholder_text="storaged",
            font=CTkFont(family='Arial', size=14)
        )
        self.addStoragedEntry.grid(row=7, column=0, padx=30, pady=(0, 15))
        self.addFormButton = CTkButton(self.addFrame, text="Add", width=160, command=self.AddBook)
        self.addFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.addFrame.grid_forget()

        #### # DelBook Form

        self.delFrame = CTkFrame(self.bookMainFrame, fg_color=('#DBDBDB', '#2B2B2B'))
        self.delFrame.grid(row=0, column=0, sticky='nsew')
        self.delFrame.grid_columnconfigure(0, weight=1)
        self.delFrame.grid_rowconfigure(8, weight=1)
        self.delLabel = CTkLabel(
            self.delFrame, text="Delete Book",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.delLabel.grid(row=0, column=0, padx=30, pady=30)
        self.delNameEntry = CTkEntry(
            self.delFrame, width=320, placeholder_text="name book",
            font=CTkFont(family='Arial', size=14)
        )
        self.delNameEntry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.delAuthorEntry = CTkEntry(
            self.delFrame, width=320, placeholder_text="author",
            font=CTkFont(family='Arial', size=14)
        )
        self.delAuthorEntry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.delPublisherEntry = CTkEntry(
            self.delFrame, width=320, placeholder_text="publisher",
            font=CTkFont(family='Arial', size=14)
        )
        self.delPublisherEntry.grid(row=3, column=0, padx=30, pady=(0, 15))
        self.delQuantityEntry = CTkEntry(
            self.delFrame, width=320, placeholder_text="quantity",
            font=CTkFont(family='Arial', size=14)
        )
        self.delQuantityEntry.grid(row=4, column=0, padx=30, pady=(0, 15))
        self.delStoragedEntry = CTkEntry(
            self.delFrame, width=320, placeholder_text="storaged",
            font=CTkFont(family='Arial', size=14)
        )
        self.delStoragedEntry.grid(row=5, column=0, padx=30, pady=(0, 15))
        self.delFormButton = CTkButton(self.delFrame, text="Delete", width=160, command=self.DelBook)
        self.delFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.delFrame.grid_forget()

        #### # User

        self.signFrame = CTkFrame(self.contentFrame, fg_color='transparent')
        self.signFrame.grid(row=0, column=0, sticky="nsew")
        self.signFrame.grid_columnconfigure(0, weight=1)
        self.signFrame.grid_rowconfigure(0, weight=0)
        self.signFrame.grid_rowconfigure(1, weight=1)
        self.signFrame.grid_rowconfigure(2, weight=0)

        ####

        self.signTopFrame = CTkFrame(self.signFrame, fg_color='transparent')
        self.signTopFrame.grid(row=0, column=0, sticky='nsew')
        self.signTopFrame.grid_columnconfigure(0, weight=1)
        self.signTopFrame.grid_rowconfigure(0, weight=1)

        self.signCenterFrame = CTkFrame(self.signFrame, fg_color='transparent')
        self.signCenterFrame.grid(row=1, column=0, sticky='nsew')
        self.signCenterFrame.grid_columnconfigure(0, weight=1)
        self.signCenterFrame.grid_rowconfigure(0, weight=1)

        self.signMainCenterFrame = CTkFrame(self.signCenterFrame, fg_color='transparent')
        self.signMainCenterFrame.grid(row=0, column=0, padx=5, sticky='nsew')
        self.signMainCenterFrame.grid_columnconfigure(0, weight=1)
        self.signMainCenterFrame.grid_rowconfigure(0, weight=1)

        self.signBottomFrame = CTkFrame(self.signFrame, fg_color='transparent')
        self.signBottomFrame.grid(row=2, column=0, sticky='nsew')
        self.signBottomFrame.columnconfigure(0, weight=1)

        ##

        self.signinButton = CTkButton(
            self.signTopFrame, text='Sign In',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.SigninEvent, state='disabled'
        )
        self.signinButton.pack(side='left', padx=(5, 0), pady=5)

        self.signupButton = CTkButton(
            self.signTopFrame, text='Sign Up',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            command=self.SignupEvent
        )
        self.signupButton.pack(side='left', padx=(5, 0), pady=5)

        self.signAccountButton = CTkButton(
            self.signTopFrame, text='',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            state='disabled'
        )
        self.signAccountButton.pack(side='right', padx=(0, 5), pady=5)
        self.signAccountButton.pack_forget()

        self.signoutButton = CTkButton(
            self.signBottomFrame, text='Sign Out',
            width=150, height=50,
            compound='left', anchor="w", font=CTkFont('Arial', size=16, weight='bold'),
            state='disabled', command=self.LogedOut
        )
        self.signoutButton.pack(side='right', padx=(0, 5), pady=5)

        ####

        # self.signBackgroundImage = CTkImage(Image.open('./icons/theme.png'), size=(1200, 600))
        # self.signBackgroundImageLabel = CTkLabel(self.signMainCenterFrame, image=self.signBackgroundImage, text=None)
        # self.signBackgroundImageLabel.grid(row=0, column=0, sticky='nsew')
        self.signBackgroundImageFrame = CTkFrame(self.signMainCenterFrame)
        self.signBackgroundImageFrame.grid(row=0, column=0, sticky='nsew')
        # BackgroundImageAutoFitContent.path = './icons/theme.png'
        self.signBackgroundImageLabel = BackgroundImageAutoFitContent(self.signBackgroundImageFrame)
        self.signBackgroundImageLabel.pack(fill=BOTH, expand=YES)

        #### # Sign in

        self.signinFrame = CTkFrame(self.signMainCenterFrame)
        self.signinFrame.grid(row=0, column=0, sticky='ns')
        self.signinFrame.grid_rowconfigure(8, weight=1)
        self.signinLabel = CTkLabel(
            self.signinFrame, text="Sign in",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.signinLabel.grid(row=0, column=0, padx=30, pady=30)
        self.usernameSigninEntry = CTkEntry(self.signinFrame, width=240, placeholder_text="username")
        self.usernameSigninEntry.grid(row=2, column=0, padx=30, pady=(15, 15))
        self.passwordSigninEntry = CTkEntry(self.signinFrame, width=240, show="*", placeholder_text="password")
        self.passwordSigninEntry.grid(row=3, column=0, padx=30, pady=(0, 15))
        self.signinFormButton = CTkButton(self.signinFrame, text="Sign in", command=self.SignIn, width=240)
        self.signinFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))

        #### # Sign up

        self.signupFrame = CTkFrame(self.signMainCenterFrame)
        self.signupFrame.grid(row=0, column=0, sticky='ns')
        self.signupFrame.grid_rowconfigure(8, weight=1)
        self.signupLabel = CTkLabel(
            self.signupFrame, text="Sign up",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.signupLabel.grid(row=0, column=0, padx=30, pady=30)
        self.idSignupEntry = CTkEntry(self.signupFrame, width=240, placeholder_text="id person")  # CCCD
        self.idSignupEntry.grid(row=2, column=0, padx=30, pady=(15, 15))
        self.signupFormButton = CTkButton(self.signupFrame, text="Sign up", command=self.CheckID, width=240)  # CheckID
        self.signupFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.signupFrame.grid_forget()

        #### # Register

        self.registerFrame = CTkFrame(self.signMainCenterFrame)
        self.registerFrame.grid(row=0, column=0, sticky='ns')
        self.registerFrame.grid_rowconfigure(8, weight=1)
        self.registerLabel = CTkLabel(
            self.registerFrame, text="Register",
            font=CTkFont(family='Arial', size=20, weight="bold")
        )
        self.registerLabel.grid(row=0, column=0, padx=30, pady=30)
        self.usernameSignupEntry = CTkEntry(self.registerFrame, width=240,
                                            placeholder_text="username")  # CCCD, state='disabled'
        self.usernameSignupEntry.grid(row=2, column=0, padx=30, pady=(15, 15))
        self.passwordSignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="password", show="*")
        self.passwordSignupEntry.grid(row=3, column=0, padx=30, pady=(15, 15))
        # self.repasswordSignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="repassword")
        # self.repasswordSignupEntry.grid(row=4, column=0, padx=30, pady=(15, 15))
        self.fullnameSignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="fullname")
        self.fullnameSignupEntry.grid(row=4, column=0, padx=30, pady=(15, 15))
        # self.genderSignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="gender")
        # self.genderSignupEntry.grid(row=6, column=0, padx=30, pady=(15, 15))
        self.genderSignupFrame = CTkFrame(self.registerFrame, width=240, fg_color='transparent')
        self.genderSignupFrame.grid(row=5, column=0, padx=30, pady=(15, 15))
        self.genderChoice = StringVar()
        self.radioMaleButton = CTkRadioButton(
            self.genderSignupFrame, text='Male',
            variable=self.genderChoice, value='male',
            font=CTkFont('Arial', size=12, weight='bold')
        )
        self.radioFemaleButton = CTkRadioButton(
            self.genderSignupFrame, text='Female',
            variable=self.genderChoice, value='female',
            font=CTkFont('Arial', size=12, weight='bold')
        )
        self.radioMaleButton.grid(row=0, column=0, sticky='e')
        self.radioFemaleButton.grid(row=0, column=1, sticky='w')
        # self.birthdaySignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="birthday (yyyy-mm-dd)")
        # self.birthdaySignupEntry.grid(row=6, column=0, padx=30, pady=(15, 15))
        self.birthdaySignupFrame = CTkFrame(self.registerFrame, width=240, fg_color='transparent')
        self.birthdaySignupFrame.grid(row=6, column=0, padx=30, pady=(15, 15))
        self.birthdateSignupEntry = CTkEntry(self.birthdaySignupFrame, width=50, placeholder_text="day")
        self.birthdateSignupEntry.grid(row=0, column=0, padx=(0, 30), sticky='e')
        self.birthmonthSignupEntry = CTkEntry(self.birthdaySignupFrame, width=50, placeholder_text="month")
        self.birthmonthSignupEntry.grid(row=0, column=1, padx=(0, 30), sticky='e')
        self.birthyearSignupEntry = CTkEntry(self.birthdaySignupFrame, width=80, placeholder_text="year")
        self.birthyearSignupEntry.grid(row=0, column=2, sticky='w')
        self.addressSignupEntry = CTkEntry(self.registerFrame, width=240, placeholder_text="address")
        self.addressSignupEntry.grid(row=7, column=0, padx=30, pady=(15, 15))
        self.registerFormButton = CTkButton(self.registerFrame, text="Register", command=self.Register, width=240)
        self.registerFormButton.grid(row=9, column=0, padx=30, pady=(15, 15))
        self.registerFrame.grid_forget()

        ####

        self.mainFrame = CTkFrame(self.signMainCenterFrame)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.mainLabel = CTkLabel(self.mainFrame, text="Home", font=CTkFont(size=20, weight="bold"))
        self.mainLabel.grid(row=0, column=0, padx=30, pady=(30, 15))
        self.backButton = CTkButton(self.mainFrame, text="Back", command=self.SigninEvent, width=240)
        self.backButton.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.mainFrame.grid_forget()

        ####
        ####

        self.SelectFrameByName('home')

        ####

        self.DisplayBooks()
        # self.DisplayStatistics()

    ############ # Method ##########    ############################

    ############ # Frame ###########

    def SelectFrameByName(self, name):
        self.homeButton.configure(fg_color=('gray75', 'gray25') if name == "home" else 'transparent')
        self.bookButton.configure(fg_color=('gray75', 'gray25') if name == "book" else 'transparent')
        self.userButton.configure(fg_color=('gray75', 'gray25') if name == "user" else 'transparent')

        ####

        if name == 'home':
            self.homeFrame.grid(row=0, column=1, sticky='nsew')
        else:
            self.homeFrame.grid_forget()
        if name == 'book':
            self.bookFrame.grid(row=0, column=1, sticky='nsew')
        else:
            self.bookFrame.grid_forget()
        if name == 'user':
            self.signFrame.grid(row=0, column=1, sticky='nsew')
        else:
            self.signFrame.grid_forget()

    def HomeButtonEvent(self):
        self.SelectFrameByName('home')

    def BookButtonEvent(self):
        self.SelectFrameByName('book')

    def UserButtonEvent(self):
        self.SelectFrameByName('user')

    def ChangeAppearanceModeEvent(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    ############ # Sign ############

    def SignIn(self):
        pass

    def Register(self):
        pass

    def CheckID(self):
        pass

    ############ # Module ##########

    def AddBook(self):
        pass
    def DelBook(self):
        pass
    def BorBook(self):
        pass
    def RtnBook(self):
        pass

    def SearchBook(self):
        self.listBooks.delete('1.0', 'end')
        for book in SAMPLE_BOOKS:
            self.listBooks.insert('end', f"{book['id']}. {book['name']}\n")

    def ListBook(self):
        self.listBooks.delete('1.0', 'end')
        for book in SAMPLE_BOOKS:
            self.listBooks.insert('end', f"{book['id']}. {book['name']}\n")

    def DisplayMembers(self):
        pass

    def DisplayStatistics(self):  # evt
        pass

    def DisplayDateForm(self):
        pass

    def Lenting(self):
        pass

    def LentInfo(self, value):
        pass

    def MemberInfo(self, value):
        pass

    def DisplayBorrowAndReturn(self, value):
        pass

    def FormInfos(self, value):
        pass

    def DisplayForm(self):
        pass

    def ReShowList(self):
        pass

    def DateCounting(self):
        pass

    ############ # UI ##############

    def AdminUI(self):
        pass

    def UserUI(self):
        pass

    def LogedOut(self):
        self.buttonHomeBook.pack_forget()
        self.buttonAddBook.pack_forget()
        self.buttonDelBook.pack_forget()
        self.buttonBorBook.pack_forget()
        self.buttonRtnBook.pack_forget()
        self.signAccountButton.pack_forget()
        # self.buttonGiveBook.pack(side='right', padx=(0, 5), pady=5)
        self.buttonHomeAccount.configure(text='Account')
        self.buttonBookAccount.pack(side='right', padx=(0, 5), pady=5)

        self.signinButton.pack(side='left', padx=(5, 0), pady=5)
        self.signupButton.pack(side='left', padx=(5, 0), pady=5)
        self.signinFrame.grid_forget()
        self.signupFrame.grid_forget()
        self.signAccountButton.pack_forget()
        self.signoutButton.configure(state='enabled')
        self.bookCenterFrame.grid_forget()

        try:
            self.tabs.delete('Member Management')
            self.tabs.delete('Borrow & Return')
            self.tabs.delete('Statistics')
        except:
            self.tabs.delete('Lenting')

        self.SigninEvent()

    ############ # Event ###########

    def SigninEvent(self):
        # print("Login pressed - username:", self.usernameEntry.get(), "password:", self.passwordEntry.get())
        self.signinButton.configure(state='disabled')
        self.signupButton.configure(state='enabled')
        self.signoutButton.configure(state='disabled')
        self.mainFrame.grid_forget()
        self.signupFrame.grid_forget()
        self.signinFrame.grid(row=0, column=0, sticky='ns')
        self.registerFrame.grid_forget()

    def SignupEvent(self):
        self.signinButton.configure(state='enabled')
        self.signupButton.configure(state='disabled')
        self.signoutButton.configure(state='disabled')
        self.mainFrame.grid_forget()
        self.signinFrame.grid_forget()
        self.signupFrame.grid(row=0, column=0, sticky='ns')

    # def SignoutEvent(self):
    #     self.signinButton.configure(state='enabled')
    #     self.signupButton.configure(state='disabled')
    #     self.singoutButton.configure(state='disabled')
    #     self.mainFrame.grid_forget()
    #     self.signinFrame.grid(row=0, column=0, sticky='ns')

    def RegisterEvent(self):
        self.signinButton.configure(state='enabled')
        self.signupButton.configure(state='disabled')
        self.signoutButton.configure(state='disabled')
        self.mainFrame.grid_forget()
        self.signinFrame.grid_forget()
        self.signupFrame.grid_forget()
        self.registerFrame.grid(row=0, column=0, sticky='ns')

    def MainEvent(self):
        self.signinButton.configure(state='disabled')
        self.signupButton.configure(state='disabled')
        self.signoutButton.configure(state='enabled')
        self.signinFrame.grid_forget()
        self.signupFrame.grid_forget()
        self.mainFrame.grid(row=0, column=0, sticky='nsew')

    ####

    def HomeListEvent(self):
        self.buttonHomeBook.configure(state='disabled')
        self.buttonAddBook.configure(state='enabled')
        self.buttonDelBook.configure(state='enabled')
        self.buttonBorBook.configure(state='enabled')
        self.buttonRtnBook.configure(state='enabled')
        self.bookCenterFrame.grid_columnconfigure(0, weight=6)
        self.bookCenterFrame.grid_columnconfigure(1, weight=4)
        self.bookCenterFrame.grid(row=0, column=0, sticky='nsew')
        self.addFrame.grid_forget()
        self.delFrame.grid_forget()
        self.borFrame.grid_forget()
        self.rtnFrame.grid_forget()
        self.ReShowList()

    def AddBookEvent(self):
        self.buttonHomeBook.configure(state='enabled')
        self.buttonAddBook.configure(state='disabled')
        self.buttonDelBook.configure(state='enabled')
        self.buttonBorBook.configure(state='enabled')
        self.buttonRtnBook.configure(state='enabled')
        self.bookMainFrame.grid_columnconfigure(0, weight=1)
        self.bookMainFrame.grid_columnconfigure(1, weight=0)
        self.bookCenterFrame.grid_forget()
        self.addFrame.grid(row=0, column=0, sticky='nsew')
        self.delFrame.grid_forget()
        self.borFrame.grid_forget()
        self.rtnFrame.grid_forget()

    def DelBookEvent(self):
        self.buttonHomeBook.configure(state='enabled')
        self.buttonAddBook.configure(state='enabled')
        self.buttonDelBook.configure(state='disabled')
        self.buttonBorBook.configure(state='enabled')
        self.buttonRtnBook.configure(state='enabled')
        self.bookMainFrame.grid_columnconfigure(0, weight=1)
        self.bookMainFrame.grid_columnconfigure(1, weight=0)
        self.bookCenterFrame.grid_forget()
        self.addFrame.grid_forget()
        self.delFrame.grid(row=0, column=0, sticky='nsew')
        self.borFrame.grid_forget()
        self.rtnFrame.grid_forget()

    def BorBookEvent(self):
        self.buttonHomeBook.configure(state='enabled')
        self.buttonAddBook.configure(state='enabled')
        self.buttonDelBook.configure(state='enabled')
        self.buttonBorBook.configure(state='disabled')
        self.buttonRtnBook.configure(state='enabled')
        self.bookMainFrame.grid_columnconfigure(0, weight=1)
        self.bookMainFrame.grid_columnconfigure(1, weight=0)
        self.bookCenterFrame.grid_forget()
        self.addFrame.grid_forget()
        self.delFrame.grid_forget()
        self.borFrame.grid(row=0, column=0, sticky='nsew')
        self.rtnFrame.grid_forget()

    def RtnBookEvent(self):
        self.buttonHomeBook.configure(state='enabled')
        self.buttonAddBook.configure(state='enabled')
        self.buttonDelBook.configure(state='enabled')
        self.buttonBorBook.configure(state='enabled')
        self.buttonRtnBook.configure(state='disabled')
        self.bookMainFrame.grid_columnconfigure(0, weight=1)
        self.bookMainFrame.grid_columnconfigure(1, weight=0)
        self.bookCenterFrame.grid_forget()
        self.addFrame.grid_forget()
        self.delFrame.grid_forget()
        self.borFrame.grid_forget()
        self.rtnFrame.grid(row=0, column=0, sticky='nsew')