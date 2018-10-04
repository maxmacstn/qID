#! python3
import time
from tkinter import *
from tkinter import messagebox
import pip

class splashscreen():
    def __init__(self):
        global count
        print("===== Launching program =====")
        self.splash = Tk()
        self.splash.iconbitmap('data\logo.ico')
        title = "qID initializing"
        self.splash.title(title)
        filelocation = "data\splash.png"
        photo = PhotoImage(file=filelocation)
        imglabel = Label(self.splash,image=photo)
        imglabel.pack()
        self.textlabel = Label(self.splash,text = "Checking Modules..")
        self.textlabel.pack()
        self.splash.after(2000, self.checkmodule)
        self.splash.mainloop()

    def checkmodule(self):
        try:
            __import__("PIL")
            print(" - Module sucessfully loaded.")
            self.splash.destroy()
            
        except:
            self.textlabel["text"] = "Downloading Module..."
            print(" - No module PILLOW found.")
            messagebox.showerror("Load module error", "Module not found. Auto starting download module.\n(Internet connection required.)")
            try:
                print(" - Upgrading PIP.")
                self.textlabel["text"] = "Download and Upgrading Module : pip"
                pip.main(['install', '--upgrade', 'pip'])
            except:
                messagebox.showerror("Load module error", "Download and Upgrading Module : pip - FAILED!!")
                print(" - Upgrading PIP Failed!!.")
                return
            self.textlabel["text"] = "Download and Install Module : Pillow"
            print(" - Installing module PILLOW using PIP.")
            pip.main(['install', "pillow"])
            

            try:
                __import__("PIL")
                self.textlabel["text"] = "Installed!"
                messagebox.showinfo("Module installed", "Essential module has been installed sucessful.\nClick OK to launch program.")
                self.splash.destroy()
                
            except:
                messagebox.showerror("Load module error", "Auto module downloading failed.\nTerminating program.")
                self.splash.destroy()

        __import__("qIDv2")
        try:
            time.sleep(5)
            MainApp()
        except:
            return

splashscreen()
