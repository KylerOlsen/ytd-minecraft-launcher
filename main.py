# Yeahbut Mar 2022

import minecraft_launcher_lib

import subprocess
import random
import webbrowser
import json
import os
import http.client
from threading  import Thread
from queue import Queue, Empty
import datetime
import io

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font as tkFont
from tkinter import PhotoImage

import mojangapi

try: from PIL import ImageTk, Image
except: Image = None

try: import win32clipboard
except: CLIPBOARD = False
else: CLIPBOARD = "win32clipboard"


DEFAULT_DIR = minecraft_launcher_lib.utils.get_minecraft_directory()#"./dir"
MAIN_LAUNCHER = None
LAUNCHER_VERSION = 'a.0.3'


class Launcher(ttk.Notebook):

    main = None

    def __init__(self, parent=None, main=True):
        if main: type(self).main = self
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        global MAIN_LAUNCHER
        MAIN_LAUNCHER = self

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.root.title("YTD Minecraft Launcher")
        self.root.iconbitmap("purplestoneicon.ico")

        self.tab_list = []

        self.launch = Launch_Frame(self)
        self.add(self.launch, text='Launch')
        self.tab_list.append(self.launch)

        self.profiles = Profiles_Frame(self)
        self.add(self.profiles, text='Profiles')
        self.tab_list.append(self.profiles)

        self.skins = Skins_Frame(self)
        self.add(self.skins, text='Skins')
        self.tab_list.append(self.skins)

        self.mods = Mods_Frame(self)
        self.add(self.mods, text='Mods')
        self.tab_list.append(self.mods)
        
        self.users = Users_Frame(self)
        self.add(self.users, text='Users')
        self.tab_list.append(self.users)

        self.versions = Versions_Frame(self)
        self.add(self.versions, text='Versions')
        self.tab_list.append(self.versions)

        self.options = Options_Frame(self)
        self.add(self.options, text='Options')
        self.tab_list.append(self.options)

        self.instainces = Instainces_Frame(self)
        self.add(self.instainces, text='Instainces')
        self.tab_list.append(self.instainces)

        self.about = About_Frame(self)
        self.add(self.about, text='About')
        self.tab_list.append(self.about)

        #self.launch.on_focus()
        self.bind("<<NotebookTabChanged>>", self.on_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_press_close)

        self.root.mainloop()
    
    def add_tab(self, tab, name):
        self.add(tab, text=name)
        self.tab_list.append(tab)
    
    def remove_tab(self, tab):
        pass

    #def on_change(self,*args):
        #for i in self.tab_list:
            #if str(i) == self.select():
                #i.on_focus()

    def on_change(self,*args):
        for i in self.tab_list:
            if str(i) == self.select():
                try: i.on_focus
                except AttributeError: pass
                else: i.on_focus()
            else:
                try: i.un_focus
                except AttributeError: pass
                else: i.un_focus()

    def on_press_close(self,*args):
        if self.root.state() != 'withdrawn':
            self.root.state('withdrawn')
        self.close_when_done()
    
    def close_when_done(self):
        if len(self.launch.minecraft_instainces) == 0 and self.root.state() == 'withdrawn':
            self.root.destroy()
        elif self.root.state() == 'withdrawn':
            self.root.after(2000, self.close_when_done)


class Launch_Frame(ttk.Frame):


    class Minecraft_Instaince(ttk.Frame):
        
        def __init__(self, cmd, options, logWindow, parent=None):
            self.root = tk.Tk() if parent is None else parent
            super().__init__(self.root, padding="3 3 3 3")
            if parent is None:
                self.root.protocol("WM_DELETE_WINDOW", self.on_press_close)
            if parent is None and not logWindow:
                self.root.overrideredirect(1)
                self.root.state('withdrawn')
            else:
                self.root.title("YTD Minecraft Launcher")

            self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)

            self.start_time = datetime.datetime.now()
            self.options = options

            self._process = subprocess.Popen(
                cmd,
                cwd = self.options["gameDirectory"],
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = None,
                close_fds = True,
                text = True
                )

            self._queue = Queue()
            self._thread = Thread(target=enqueue_output, args=(self._process.stdout, self._queue))
            self._thread.daemon = True # thread dies with the program
            self._thread.start()

            self.text = tk.Text(self, width=80, height=20, wrap="none")

            self.ys = ttk.Scrollbar(self, orient = 'vertical', command = self.text.yview)
            self.xs = ttk.Scrollbar(self, orient = 'horizontal', command = self.text.xview)
            self.text['yscrollcommand'] = self.ys.set
            self.text['xscrollcommand'] = self.xs.set

            self.text.insert('1.0', 'Launcher Starting Minecraft...\n')
            self.text['state'] = 'disabled'

            self.text.grid(column=0, row=1, sticky='w')
            self.xs.grid(column = 0, row = 2, sticky = 'we')
            self.ys.grid(column = 1, row = 1, sticky = 'ns')

            self.root.after(100, self.loop)

        def on_press_close(self,*args):
            if self.root.state() != 'withdrawn':
                self.root.state('withdrawn')

        def loop(self,*args):
            poll = self._process.poll()
            if poll is not None:
                #print(poll)
                if poll == 0: return self.close()
                else: return MAIN_LAUNCHER.launch.crash(self)
            try: line = self._queue.get_nowait()
            except Empty: self.root.after(100, self.loop)#time.sleep(0.1)
            else:
                if line == None: self.root.after(10, self.loop)
                else:
                    #print(line[:-1])
                    self.text['state'] = 'normal'
                    self.text.insert('end',line)
                    self.text['state'] = 'disabled'
                    self.root.after(10, self.loop)
        
        def kill(self,*args):
            self._process.kill()
        
        def terminate(self,*args):
            self._process.terminate()

        def open_log(self,*args):
            if self.root.state() != 'normal':
                self.root.state('normal')
        
        def close(self,*args):
            MAIN_LAUNCHER.launch.minecraft_instainces.remove(self)
            MAIN_LAUNCHER.instainces.update()
            if self.root.state() == 'withdrawn': self.root.destroy()


    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        #self.minecraft_directory = ".\\dir"
        self.minecraft_instainces = []

        ttk.Label(self, text="Username").grid(row=1, column=3, sticky=tk.W)
        self.username = tk.StringVar()
        self.username_entry = ttk.Combobox(self, textvariable=self.username)
        self.username_entry.grid(row=1, column=2, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Profile").grid(row=2, column=3, sticky=tk.W)
        self.profile_names = tk.StringVar()
        self.profile_names_entry = ttk.Combobox(self, textvariable=self.profile_names)
        self.profile_names_entry.grid(row=2, column=2, sticky=tk.W)
        self.profile_names_entry.bind('<<ComboboxSelected>>', self.on_profile_change) 

        self.version = ttk.Label(self, text="")
        self.version.grid(row=3, column=2, sticky=tk.W)

        self.online = ttk.Label(self, text="")
        self.online.grid(row=3, column=3, sticky=tk.W)

        ttk.Button(self, text="Launch", command=self.launch).grid(row=4, column=2, columnspan=2, sticky=(tk.W, tk.E))

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

    def on_focus(self):
        
        #users = []
        #for i in self.root.users.users:
        #    users.append(i["name"])
        #self.username_entry['values'] = users
        #if len(users) > 0: self.username_entry.current(0)
        self.root.users.load_list_users(self.username_entry)
        
        #versions = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_directory)
        #installed_versions = []
        #for i in versions:
        #    installed_versions.append(i['id'])
        #self.version_entry['values'] = installed_versions
        #if len(installed_versions) > 0: self.version_entry.current(0)
        self.root.profiles.load_list_profiles(self.profile_names_entry,select=0 if self.root.profiles.active is None else self.root.profiles.active)
        
        self.version["text"] = "Version: "+self.root.profiles.get_profile(self.profile_names.get())["version"]

        self.online["text"] = "Online" if have_internet() else "Offline"

        #self.root.bind("<Return>", self.launch)

    def launch(self,*args):
        profile_name = self.profile_names.get()
        profile = self.root.profiles.get_profile(profile_name)

        login_data = self.root.users.get_user(self.username.get())
        options = {}
        if login_data is not None:
            if have_internet(): login_data = self.root.users.auth_user(login_data["name"])
            options["username"] = login_data["name"]
            options["uuid"] = login_data["id"]
            options["token"] = login_data["access_token"]
        else:
            options["username"] = f"Player{random.randint(100, 999)}" if self.username.get() == "" else self.username.get()
            options["uuid"] = "0"
            options["token"] = "0"
            options["demo"] = self.root.options.forceDemo
        if "server" in profile:
            if ":" in profile["server"]:
                options["server"] = profile["server"].split(":")[0]
                options["port"] = profile["server"].split(":")[1]
            else:
                options["server"] = profile["server"]
        if "jvmArguments" in profile:
            options["jvmArguments"] = profile["jvmArguments"].split(" ")
        if "gameDirectory" in profile:
            options["gameDirectory"] = profile["gameDirectory"]
        else:
            options["gameDirectory"] = self.root.options.minecraftDirectory

        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(profile["version"], self.root.options.minecraftDirectory, options)

        instaince_options = {
            "gameDirectory" : options["gameDirectory"],
            "username" : options["username"],
            "profile" : profile_name,
            "version" : profile["version"],
        }

        self.minecraft_instainces.append(self.Minecraft_Instaince(minecraft_command, instaince_options, self.root.options.logWindow))
        if not self.root.options.keepMainWindow: self.root.on_press_close()
        
        #if self.root.options.logWindow:
        #    self.minecraft_instainces.append(self.Minecraft_Instaince(minecraft_command, options))
        #else:
        #    subprocess.Popen(
        #        minecraft_command,
        #        cwd = options["gameDirectory"],
        #        stdin = subprocess.PIPE,
        #        stdout = subprocess.PIPE,
        #        stderr = None,
        #        close_fds = True,
        #        text = True
        #        )

        #subprocess.Popen(minecraft_command, cwd=options["gameDirectory"])

    def crash(self,instance):
        self.root.root.state('normal')
        messagebox.showerror(message='Oops! Minecraft Crashed!', title="YTD MC Launcher")

        self.minecraft_instainces.remove(instance)
        
        if instance.root.state() == 'withdrawn': instance.root.destroy()
        self.root.instainces.update()

        #self.root.root.after(5000,lambda: self.minecraft_instainces.remove(instance))

        #time.sleep(4)
        #self.minecraft_instainces.remove(instance)

    def on_profile_change(self,*args):
        self.root.profiles.set_active_profile(self.profile_names.get())
        self.on_focus()


class Profiles_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.active = None
        self.profiles = []
        self.load_profiles()

        #self.minecraft_directory = ".\\dir"

        self.profile_names = tk.StringVar()
        self.profile_names_entry = ttk.Combobox(self, textvariable=self.profile_names)
        self.profile_names_entry.grid(column=2, row=1)
        self.profile_names_entry.bind('<<ComboboxSelected>>', self.on_profile_change)
        ttk.Label(self, text="Profile").grid(column=3, row=1, sticky=tk.W)

        self.version = tk.StringVar()
        self.version_entry = ttk.Combobox(self, textvariable=self.version)
        self.version_entry.grid(column=2, row=2)
        ttk.Label(self, text="Version").grid(column=3, row=2, sticky=tk.W)

        self.jvmArguments = tk.StringVar()
        ttk.Entry(self, textvariable=self.jvmArguments).grid(column=2, row=3)
        ttk.Label(self, text="jvmArgs").grid(column=3, row=3, sticky=(tk.W, tk.E))

        self.gameDirectory = tk.StringVar()
        ttk.Entry(self, textvariable=self.gameDirectory).grid(column=2, row=4)
        gamedir = ttk.Label(self, text="Game Dir")
        gamedir.grid(column=3, row=4, sticky=(tk.W, tk.E))
        gamedir.bind('<1>', func=self.get_directory)
        font = tkFont.Font(font="TkDefaultFont")
        font.configure(underline = True)
        gamedir.configure(font=font)

        self.server = tk.StringVar()
        ttk.Entry(self, textvariable=self.server).grid(column=2, row=5)
        ttk.Label(self, text="Server").grid(column=3, row=5, sticky=(tk.W, tk.E))

        ttk.Button(self, text="Save", command=self.save).grid(column=3, row=6, sticky=tk.W)


        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
    
    def get_directory(self,*args):
        if "gameDirectory" in self.get_active_profile():
            directorystart = self.get_active_profile()["gameDirectory"]
        else: directorystart = self.root.options.minecraftDirectory
        directory = filedialog.askdirectory(initialdir=directorystart)
        if directory != "":
            self.gameDirectory.set(directory)

    def on_profile_change(self,*args):
        self.set_active_profile(self.profile_names.get())
        self.on_focus()

    def on_focus(self):
        if self.active is None:
            self.load_list_profiles(self.profile_names_entry)
            self.root.versions.load_list_versions(self.version_entry)
            self.jvmArguments.set("")
            self.gameDirectory.set("")
            self.server.set("")
        else:
            self.load_list_profiles(self.profile_names_entry,select=self.active)
            self.root.versions.load_list_versions(self.version_entry,select=self.get_active_profile()["version"])
            self.jvmArguments.set(self.get_active_profile()["jvmArguments"] if "jvmArguments" in self.get_active_profile() else "")
            self.gameDirectory.set(self.get_active_profile()["gameDirectory"] if "gameDirectory" in self.get_active_profile() else "")
            self.server.set(self.get_active_profile()["server"] if "server" in self.get_active_profile() else "")
        
    def load_list_profiles(self,entry,select=0):
        profiles = []
        for i in self.profiles:
            profiles.append(i["name"])
        entry['values'] = profiles
        if select is not None:
            if type(select) is not int: entry.current(profiles.index(select))
            elif len(profiles) > select: entry.current(select)

    def load_profiles(self):
        try: data = json.load(open("ytd_launcher_profiles.json"))
        except:
            self.active = None
            self.profiles = []
        else:
            if "active" in data: self.active = data["active"]
            else: self.active = None
            if "profiles" in data: self.profiles = data["profiles"]
            else: self.profiles = []
            
            if self.active not in self.get_profile_names():
                self.active = None

    def save_profiles(self):
        data = {}
        if len(self.profiles) > 0: data["profiles"] = self.profiles
        if self.active is not None: data["active"] = self.active
        json.dump(data, open("ytd_launcher_profiles.json",'w'), indent=4)

    def save(self):
        profile_info = self.organize_profile_info()
        if profile_info["name"] in self.get_profile_names():
            self.update_profile(profile_info)
        else:
            self.add_profile(profile_info)

    def organize_profile_info(self):
        profile_info = {}
        profile_info["name"] = self.profile_names.get().strip()
        profile_info["version"] = self.version.get().strip()
        if self.jvmArguments.get().strip() != "": profile_info["jvmArguments"] = self.jvmArguments.get().strip()
        if self.gameDirectory.get().strip() != "": profile_info["gameDirectory"] = self.gameDirectory.get().strip()
        if self.server.get().strip() != "": profile_info["server"] = self.server.get().strip()
        return profile_info

    def add_profile(self,profile_info):
        self.profiles.append(profile_info)
        self.save_profiles()

    def update_profile(self,profile_info):
        for i in range(len(self.profiles)):
            if self.profiles[i]['name'] == profile_info['name']:
                self.profiles[i] = profile_info
                self.save_profiles()
                return

    def get_profile(self,profile_name):
        for i in self.profiles:
            if i['name'] == profile_name:
                return i

    def get_profile_names(self):
        names = []
        for i in self.profiles:
            names.append(i['name'])
        return names

    def get_active_profile(self):
        if self.active is not None:
            return self.get_profile(self.active)

    def set_active_profile(self,profile_name):
        if profile_name in self.get_profile_names():
            self.active = profile_name
            self.save_profiles()


class Skins_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=1)

        ttk.Label(self, text="Skin Changer").grid(row=1, column=1, columnspan=4, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Username").grid(row=2, column=4, sticky=tk.W)
        self.username = tk.StringVar()
        self.username_entry = ttk.Combobox(self, textvariable=self.username)
        self.username_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Button(self, text="Download", command=self.download_skin).grid(row=3, column=1, sticky=(tk.W))
        ttk.Button(self, text="Save", command=self.save_skin).grid(row=3, column=2, sticky=(tk.W))
        ttk.Button(self, text="Upload", command=self.upload_skin).grid(row=3, column=3, sticky=(tk.W))
        ttk.Button(self, text="Open", command=self.select_skin).grid(row=3, column=4, sticky=(tk.W))

        self.skin = None
        self.skin_variant = tk.StringVar()
        self.skin_image = None
        ttk.Label(self, text="Skin:").grid(row=4, column=1, sticky=tk.W)
        skin_var_entry = ttk.Combobox(self, textvariable=self.skin_variant, width=6)
        skin_var_entry.grid(row=4, column=2, sticky=(tk.W))
        skin_var_entry['values'] = mojangapi.SKIN_VARIANTS
        self.skin_label = ttk.Label(self)
        self.skin_label.grid(row=4, column=3, columnspan=2, sticky=tk.W)

        ttk.Button(self, text="Download", command=self.download_cape).grid(row=5, column=1, sticky=(tk.W))
        ttk.Button(self, text="Save", command=self.save_cape).grid(row=5, column=2, sticky=(tk.W))

        self.cape = None
        self.cape_alias = tk.StringVar()
        self.cape_image = None
        ttk.Label(self, text="Cape:").grid(row=6, column=1, sticky=tk.W)
        self.cape_label = ttk.Label(self)
        self.cape_label.grid(row=6, column=2, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
    
    def on_focus(self):
        self.root.users.load_list_users(self.username_entry)
        self.after(0,self.update)
    
    def update(self):
        if have_internet():
            self.download_skin()
            self.download_cape()
    
    def display_skin(self):
        if self.skin is not None:
            if Image is None: self.skin_image = PhotoImage(data=self.skin, format='png')
            else: self.skin_image = ImageTk.PhotoImage(Image.open(io.BytesIO(self.skin)))
            self.skin_label['image'] = self.skin_image
        else: self.skin_label['image'] = ""

    def download_skin(self):
        if have_internet():
            try: user = mojangapi.username_to_uuid(self.username.get())
            except: pass
            else: data = mojangapi.uuid_to_skin(user['id'])
            self.skin = data
            #print(mojangapi.uuid_to_profile_texture(user['id']))
        else: no_internet_warning()
        self.display_skin()

    def save_skin(self):
        if self.skin is not None:
            with filedialog.asksaveasfile(initialfile = f'{self.username.get()}_skin.png', mode='wb', defaultextension=".png",filetypes=[("All Files","*.*"),("Images","*.png")]) as file:
                if file is None: return
                file.write(self.skin)

    def upload_skin(self):
        if have_internet():
            username = self.username.get()
            if self.root.users.has_user(username):
                self.root.users.auth_user(username)
                user = self.root.users.get_user(username)
                variant = self.skin_variant.get()
                if variant not in mojangapi.SKIN_VARIANTS:
                    messagebox.showerror(message=f"The skin variant '{variant}' is inavlid!", title="YTD MC Launcher")
                    return
                mojangapi.upload_skin(user['access_token'], variant, self.skin)
            else:
                messagebox.showerror(message=f"The user '{username}' is not logged in!", title="YTD MC Launcher")
        else: no_internet_warning()

    def select_skin(self):
        with filedialog.askopenfile(mode='rb', defaultextension=".png",filetypes=[("All Files","*.*"),("Images","*.png")]) as file:
            if file is None: return
            self.skin = file.read()
        self.display_skin()
    
    def display_cape(self):
        if self.cape is not None:
            if Image is None: self.cape_image = PhotoImage(data=self.cape, format='png')
            else: self.cape_image = ImageTk.PhotoImage(Image.open(io.BytesIO(self.cape)))
            self.cape_label['image'] = self.cape_image
        else: self.cape_label['image'] = ""

    def download_cape(self):
        if have_internet():
            try: user = mojangapi.username_to_uuid(self.username.get())
            except: pass
            else: data = mojangapi.uuid_to_cape(user['id'])
            self.cape = data
        else: no_internet_warning()
        self.display_cape()

    def save_cape(self):
        if self.cape is not None:
            with filedialog.asksaveasfile(initialfile = f'{self.username.get()}_cape.png', mode='wb', defaultextension=".png",filetypes=[("All Files","*.*"),("Images","*.png")]) as file:
                if file is None: return
                file.write(self.cape)


class Mods_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(self, text="Fabric Mod Installer WIP").grid(row=1, column=3, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
    
    def on_focus(self):
        pass


class Users_Frame(ttk.Frame):

    client_id = "3c79171b-0027-479c-9646-9b394bf04930"
    redirect_url = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    client_secret = ""

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.users = []
        self.load_users()

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        ttk.Button(self, text="Login", command=self.login).grid(column=3, row=1, sticky=tk.W)

        self.backup_url = tk.StringVar()
        self.backup_url_entry = ttk.Entry(self, textvariable=self.backup_url)
        self.backup_url_entry.grid(column=2, row=2, sticky=(tk.W, tk.E))

        self.username = tk.StringVar()
        self.username_entry = ttk.Combobox(self, textvariable=self.username)
        self.username_entry.grid(column=2, row=3, sticky=(tk.W, tk.E))
        ttk.Button(self, text="Logout", command=self.logout).grid(column=3, row=3, sticky=tk.W)

        ttk.Label(self, text="Microsoft Account").grid(column=2, row=1, sticky=tk.W)
        ttk.Label(self, text="Backup URL").grid(column=3, row=2, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
    def on_focus(self):
        self.load_list_users(self.username_entry)
        #self.root.bind("<Return>", self.login)
    
    def load_list_users(self,entry,select=0):
        users = []
        for i in self.users:
            users.append(i["name"])
        entry['values'] = users
        if select is not None:
            if type(select) is not int: entry.current(users.index(select))
            elif len(users) > select: entry.current(select)

    def login(self,*args):
        if not have_internet():
            no_internet_warning()
            return
        secret_id = self.client_id
        if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(self.backup_url.get()):
            try:
                auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(self.backup_url.get())
                user_info = minecraft_launcher_lib.microsoft_account.complete_login(secret_id, self.client_secret, self.redirect_url, auth_code)
                self.add_user(user_info)
            except:
                messagebox.showerror(title="Login Failed",message="An Error Occured, Unable to login!")
                raise
            else: messagebox.showinfo(title="Login Success",message="You have successfully login.")
        else:
            login_url = minecraft_launcher_lib.microsoft_account.get_login_url(self.client_id, self.redirect_url)
            webbrowser.open(login_url)
            if CLIPBOARD:
                result = messagebox.askokcancel(title="Login",message="Please login and copy the final url.")
                if result:
                    win32clipboard.OpenClipboard()
                    try: data = win32clipboard.GetClipboardData()
                    except:
                        messagebox.showerror(title="Login Failed",message="The system clipboard could not be read. Please enter the url into the backup url field.")
                        win32clipboard.CloseClipboard()
                    else:
                        win32clipboard.CloseClipboard()
                        if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(data):
                            try:
                                auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(data)
                                user_info = minecraft_launcher_lib.microsoft_account.complete_login(secret_id, self.client_secret, self.redirect_url, auth_code)
                                self.add_user(user_info)
                            except:
                                messagebox.showerror(title="Login Failed",message="An Error Occured, Unable to login!")
                                raise
                            else: messagebox.showinfo(title="Login Success",message="You have successfully login.")
                        else:
                            messagebox.showerror(title="Login Failed",message="The url was not found in the clipboard. Please enter the url into the backup url field or try again.")
            else:
                messagebox.showinfo(title="Login",message="Please login and enter the final url into the backup url field.")
    
    def logout(self,*args):
        for i in range(len(self.users)):
            if self.users[i]["name"] == self.username.get():
                del self.users[i]
                self.save_users()
                return

    def load_users(self):
        try: self.users = json.load(open("ytd_launcher_users.json"))
        except: self.users = []

    def save_users(self):
        json.dump(self.users, open("ytd_launcher_users.json",'w'), indent=4)

    def add_user(self,user_info):
        if self.get_user(user_info['name']) is None:
            self.users.append(user_info)
        else:
            for i in range(len(self.users)):
                if self.users[i]['name'] == user_info['name']:
                    self.users[i] = user_info
        self.save_users()

    def has_user(self,username):
        for i in self.users:
            if i['name'] == username:
                return True
        return False

    def get_user(self,username):
        for i in self.users:
            if i['name'] == username:
                return i
    
    def auth_user(self,username):
        secret_id = self.client_id
        user = self.get_user(username)
        online = have_internet()
        if user is None: raise NameError
        elif online:
            #print(user)
            data = minecraft_launcher_lib.microsoft_account.refresh_authorization_token(self.client_id,self.client_secret,self.redirect_url,user['refresh_token'])
            user['access_token'] = data['access_token']
            user['refresh_token'] = data['refresh_token']
            data = minecraft_launcher_lib.microsoft_account.authenticate_with_xbl(user['access_token'])
            xbl_token = data['Token']
            userhash = data['DisplayClaims']['xui'][0]['uhs']
            xsts_token = minecraft_launcher_lib.microsoft_account.authenticate_with_xsts(xbl_token)['Token']
            data = minecraft_launcher_lib.microsoft_account.authenticate_with_minecraft(userhash,xsts_token)
            user['access_token'] = data['access_token']
            #print(data)
            self.save_users()
            return user


class Versions_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        ttk.Label(self, text="Install Versions").grid(row=1, column=1, columnspan=2, sticky=tk.W)

        self.version = tk.StringVar()
        self.version_entry = ttk.Combobox(self, textvariable=self.version)#, width=15)
        self.version_entry.grid(column=2, row=2)

        #ttk.Label(self, text="Version").grid(column=3, row=1, sticky=tk.W)
        #version_frame = ttk.Frame(self)
        #version_frame.grid(column=3, row=1)
        self.version_type = tk.StringVar()
        self.version_type_entry = ttk.Combobox(self, textvariable=self.version_type, width=10)#, command=self.on_focus)
        self.version_type_entry.grid(column=3, row=2)
        self.version_type_entry["values"] = ['release','snapshot','old_beta','old_alpha','fabric']
        self.version_type_entry.current(0)
        self.version_type_entry.bind('<<ComboboxSelected>>', self.on_focus) 
        #ttk.Radiobutton(version_frame, text='A', variable=self.version_type, value='old_alpha', command=self.on_focus).grid(column=1, row=1)
        #ttk.Radiobutton(version_frame, text='B', variable=self.version_type, value='old_beta', command=self.on_focus).grid(column=2, row=1)
        #ttk.Radiobutton(version_frame, text='S', variable=self.version_type, value='snapshot', command=self.on_focus).grid(column=3, row=1)
        #ttk.Radiobutton(version_frame, text='R', variable=self.version_type, value='release', command=self.on_focus).grid(column=4, row=1)
        #self.version_type.set('release')
        
        ttk.Button(self, text="Install", command=self.install).grid(row=3, column=3, sticky=tk.W)

        self.progress = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress.grid(row=4, column=2, columnspan=2, sticky=tk.W)
        self.max_progress = 100

        self.progress_text = ttk.Label(self, text="")
        self.progress_text.grid(row=3, column=2, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

    def on_focus(self,*args):
        if have_internet():
            self.load_list_avalible_versions(self.version_entry,release_type=self.version_type.get())
    
    def set_text(self,s):
        self.progress_text["text"] = s
        self.update()

    def set_progress(self,val):
        if self.max_progress != 0: perc = val / self.max_progress * 100
        else: perc = 1
        self.progress['value'] = perc
        self.update()

    def set_max_progress(self,val):
        self.max_progress = val

    def install(self,*args):
        if not have_internet():
            no_internet_warning()
            return
        callback = {
            "setStatus": self.set_text,
            "setProgress": self.set_progress,
            "setMax": self.set_max_progress,
        }
        ver = self.version.get()
        if self.version_type.get() == "fabric":
            minecraft_launcher_lib.fabric.install_fabric(ver,self.root.options.minecraftDirectory,callback=callback)
        else:
            minecraft_launcher_lib.install.install_minecraft_version(ver,self.root.options.minecraftDirectory,callback)
    
    def load_list_versions(self,entry,directory=None,select=0):
        if directory is None: directory = self.root.options.minecraftDirectory
        versions = minecraft_launcher_lib.utils.get_installed_versions(directory)
        installed_versions = []
        for i in reversed(versions):
            installed_versions.append(i['id'])
        entry['values'] = installed_versions
        if select is not None:
            if type(select) is not int: entry.current(installed_versions.index(select))
            elif len(installed_versions) > select: entry.current(select)
    
    def load_list_avalible_versions(self,entry,release_type="release",select=0):
        if release_type == "fabric":
            avalible_versions = minecraft_launcher_lib.fabric.get_stable_minecraft_versions()
        else:
            versions = minecraft_launcher_lib.utils.get_version_list()
            avalible_versions = []
            if type(release_type) is str: release_type = [release_type,]
            for i in versions:
                if i['type'] in release_type:
                    avalible_versions.append(i['id'])
        entry['values'] = avalible_versions
        if select is not None:
            if type(select) is not int: entry.current(avalible_versions.index(select))
            elif len(avalible_versions) > select: entry.current(select)


class Options_Frame(ttk.Frame):

    _default_options = {
        "minecraftDirectory" : os.path.realpath(DEFAULT_DIR),
        "logWindow" : True,
        "keepMainWindow" : True,
        "forceDemo" : True,
        "onlineTimeout" : 5000,
        "offlineWarning" : True,
    }
    
    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=1)

        self._options = {}
        self.load()

        ttk.Label(self, text="Launcher Options").grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        self._minecraftDirectory = tk.StringVar()
        ttk.Entry(self, textvariable=self._minecraftDirectory).grid(column=2, row=2, sticky=(tk.W, tk.E))
        minecraftdir = ttk.Label(self, text="Minecraft Directory")
        minecraftdir.grid(column=3, row=2, sticky=tk.W)
        minecraftdir.bind('<1>', func=self.get_directory)
        font = tkFont.Font(font="TkDefaultFont")
        font.configure(underline = True)
        minecraftdir.configure(font=font)

        self._logWindow = tk.BooleanVar()
        ttk.Checkbutton(self, text='Open Log Window', variable=self._logWindow).grid(column=2, row=3, sticky=(tk.W, tk.E))
        self._keepMainWindow = tk.BooleanVar()
        ttk.Checkbutton(self, text='Keep Launcher Open', variable=self._keepMainWindow).grid(column=3, row=3, sticky=(tk.W, tk.E))

        self._onlineTimeout = tk.StringVar()
        ttk.Spinbox(self, textvariable=self._onlineTimeout).grid(column=2, row=4, sticky=(tk.W, tk.E))
        ttk.Label(self, text="Online Test Timeout (ms)").grid(column=3, row=4, sticky=tk.W)

        ttk.Button(self, text="Save", command=self.save).grid(column=3, row=5, sticky=tk.W)

        ttk.Button(self, text="Quit Launcher", command=self.quit).grid(column=2, row=5, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

    def on_focus(self):
        self._minecraftDirectory.set(self._options["minecraftDirectory"])
        self._logWindow.set(self._options["logWindow"])
        self._keepMainWindow.set(self._options["keepMainWindow"])
        self._onlineTimeout.set(self._options["onlineTimeout"])
    
    def save(self):
        #self._options = {}
        if self._minecraftDirectory.get() == "": self._options["minecraftDirectory"] = self._default_options["minecraftDirectory"]
        else: self._options["minecraftDirectory"] = os.path.realpath(self._minecraftDirectory.get())
        self._options['logWindow'] = self._logWindow.get()
        self._options['keepMainWindow'] = self._keepMainWindow.get()
        self._options['onlineTimeout'] = int(self._onlineTimeout.get())
        json.dump(self._options, open("ytd_launcher_options.json",'w'), indent=4)

    def quit(self):
        self.root.root.destroy()

    def load(self):
        try: data = json.load(open("ytd_launcher_options.json"))
        except:
            self._options = self._default_options
        else: self._options = data
        for i in self._default_options:
            if i not in self._options:
                self._options[i] = self._default_options[i]
    
    def get_directory(self,*args):
        directorystart = self.minecraftDirectory
        directory = filedialog.askdirectory(initialdir=directorystart)
        if directory != "":
            self._minecraftDirectory.set(directory)

    @property
    def minecraftDirectory(self): return self._options["minecraftDirectory"]
    @property
    def logWindow(self): return self._options["logWindow"]
    @property
    def keepMainWindow(self): return self._options["keepMainWindow"]
    @property
    def forceDemo(self): return self._options["forceDemo"]
    @property
    def onlineTimeout(self): return self._options["onlineTimeout"]
    @property
    def offlineWarning(self): return self._options["offlineWarning"]


class Instainces_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        self.instaince_list = ttk.Treeview(self, columns=('user','profile','version'), height=10)
        self.instaince_list.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Button(self, text="End Task", command=self.kill).grid(row=2, column=1, sticky=(tk.W, tk.E))
        ttk.Button(self, text="Close", command=self.terminate).grid(row=2, column=2, sticky=(tk.W, tk.E))
        ttk.Button(self, text="Log Window", command=self.log).grid(row=2, column=3, sticky=(tk.W, tk.E))
        
        self.instaince_list['columns'] = ('user','profile','version')

        #self.list.grid(row=1, column=1, sticky=tk.W)
        self.instaince_list.column('#0', width=85, anchor='w')
        self.instaince_list.heading('#0', text='#')
        self.instaince_list.column('user', width=125, anchor='w')
        self.instaince_list.heading('user', text='User')
        self.instaince_list.column('profile', width=125, anchor='w')
        self.instaince_list.heading('profile', text='Profile')
        self.instaince_list.column('version', width=175, anchor='w')
        self.instaince_list.heading('version', text='Version')
        
        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

    def on_focus(self):
        self.update()

    def update(self):
        self._clear()

        for i in self.root.launch.minecraft_instainces:
            self.instaince_list.insert('', 'end',
            text=i.start_time.strftime("%b")[0]+i.start_time.strftime(" %d-%H:%M"),
            values=(
                    i.options['username'],
                    i.options['profile'],
                    i.options['version'],
                )
            )
    
    def _clear(self):
        for i in self.instaince_list.get_children():
            self.instaince_list.delete(i)
    
    def get_selected(self):
        sel = self.instaince_list.selection()
        for i in self.root.launch.minecraft_instainces:
            if i.start_time.strftime("%b")[0]+i.start_time.strftime(" %d-%H:%M") == self.instaince_list.item(sel[0])['text']:
                return i
    
    def kill(self, *args):
        self.get_selected().kill()
    
    def terminate(self, *args):
        self.get_selected().terminate()
    
    def log(self, *args):
        self.get_selected().open_log()


class About_Frame(ttk.Frame):

    def __init__(self, parent=None):
        self.root = tk.Tk() if parent is None else parent
        super().__init__(self.root, padding="3 3 12 12")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        ttk.Label(self, text="YTD Minecraft Launcher").grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(self, text="Created by Yeahbut").grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(self, text=f"Launcher Version: {LAUNCHER_VERSION}").grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Online Conection Status:").grid(row=4, column=1, sticky=tk.W)
        self.online = ttk.Label(self, text="")
        self.online.grid(row=4, column=2, sticky=tk.W)

        ttk.Label(self, text="Quit Launcher:").grid(row=5, column=1, sticky=tk.W)
        ttk.Button(self, text="Quit Launcher", command=self.quit).grid(column=2, row=5, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
    
    def on_focus(self):
        self.online["text"] = "Online" if have_internet() else "Offline"

    def quit(self):
        self.root.root.destroy()


def getHttp(url,j=False,t=False):
    import urllib
    if j: return json.loads(urllib.request.urlopen(url).read().decode('utf8'))
    elif t: return urllib.request.urlopen(url).read().decode('utf8')
    else: return urllib.request.urlopen(url).read()

def enqueue_output(out, queue):
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
    except ValueError: queue.put(None)
    finally: out.close()

def no_internet_warning():
    if MAIN_LAUNCHER.options.offlineWarning:
        messagebox.showwarning(message=f"No internet connection!", title="YTD MC Launcher")

_have_internet_state = None

def have_internet():#sure=False):
    global _have_internet_state
    #if not sure and MAIN_LAUNCHER.options.onlineTimeout > 1000 and _have_internet_state is not None:
    #    MAIN_LAUNCHER.after(0, lambda: have_internet(True))
    #    return _have_internet_state
    conn = http.client.HTTPSConnection("8.8.8.8", timeout=MAIN_LAUNCHER.options.onlineTimeout/1000)
    try:
        conn.request("HEAD", "/")
        _have_internet_state = True
        return True
    except Exception:
        if _have_internet_state is None or _have_internet_state: no_internet_warning()
        _have_internet_state = False
        return False
    finally:
        conn.close()

Launcher()
