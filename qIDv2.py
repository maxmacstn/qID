#! python3.5
from tkinter import *
import tkinter as tk
from tkinter import filedialog,messagebox
from tkinter.ttk import *
import glob, os
import sys
import pickle
from PIL import Image, ImageTk,ImageEnhance,ImageFilter
import PIL.Image


appversion = "2.0 "
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here



class process():
    def __init__(self,image,editlist,filtervalue,iswatermark,watermarkfilename,size,issharpen):
        self.export = image

        self.editlist = editlist
        filename = filedialog.asksaveasfile(mode='w',initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))


        if filename is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return

        print("===== Exporting =====")


        count = 0
        if size == 0:
            print(" - Export at original size")

        else:
            print(" - Export at size = ", size)
            self.export.thumbnail((size,size),PIL.Image.ANTIALIAS)

        for i in self.editlist:
            percent = format(count* 100/len(self.editlist),'.2f')
            print(" - Progress = ",percent,'%')
            key = i[0]
            value = i[1]
            if key == 'b':
                self.enhancer = ImageEnhance.Brightness(self.export)
                self.export = self.enhancer.enhance(value)
                print(" > Updated :",key," Value :",value)
            if key == 'c':
                self.enhancer = ImageEnhance.Contrast(self.export)
                self.export = self.enhancer.enhance(value)
                print(" > Updated :",key," Value :",value)
            if key == 's':
                self.enhancer = ImageEnhance.Color(self.export)
                self.export = self.enhancer.enhance(value)
                print(" > Updated :",key," Value :",value)
            count += 1

        if filtervalue == 'CONTOUR':
            self.export = self.export.filter(ImageFilter.CONTOUR)
            print(" - adding filter", filtervalue)

        if filtervalue == 'DETAIL':
            self.export = self.export.filter(ImageFilter.DETAIL)
            print(" - adding filter", filtervalue)

        if filtervalue == 'BLUR':
            self.export = self.export.filter(ImageFilter.GaussianBlur(radius = self.getblurvalue()))
            print(" - adding filter", filtervalue)

        if filtervalue == 'EMBOSS':
            self.export = self.export.filter(ImageFilter.EMBOSS)
            print(" - adding filter", filtervalue)

        if filtervalue == 'SMOOTH':
            self.export = self.export.filter(ImageFilter.SMOOTH)
            print(" - adding filter", filtervalue)


        if issharpen :
            print(" - adding UnsharpMask")
            self.export = self.export.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))

        #watermark processing


        if watermarkfilename != 'none' and iswatermark:
            print(" - adding watermark")
            watermark = PIL.Image.open(watermarkfilename)
            width,height = watermark.size
            export_w,export_h = self.export.size
            watermarkwidth = export_w*0.07
            watermark.thumbnail((watermarkwidth,watermarkwidth))
            width,height = watermark.size
            pos = (export_w-int(export_w*0.1),export_h-int(export_h*0.11))
            self.export.paste(watermark,pos)

        filename = str(filename)

        filename = (filename.split("name='",1)[1])
        filename = (filename.split("' mode='",1)[0])
        os.remove(filename)
        if filename[-4:] != '.jpg':
            filename = filename + '.jpg'

        self.export.save(filename)
        print(" - Progress =  100.00 %  Done!!")
        print("\n - Image exporting sucess. Saved at : ",filename)
        messagebox.showinfo("Saved", "image has been exported")

    def getblurvalue(self):
        width,height = self.export.size
        if width > 5000:
            return 9
        if width >= 2048:
            return 8
        if width >=1080:
            return 6
        if width >= 480:
            return 4
        if width >= 240:
            return 3
        else:
            return 2


class MainApp():
    def __init__(self):
        self.colorfilter_list = ['NONE','BLUR','CONTOUR','DETAIL','SMOOTH','EMBOSS']
        self.exportwidth = ['Original','2048px','1080px','480px','240px']
        #initilize
        print("===== Welcome to qID V.",appversion,"=====")
        self.root = Tk()
        self.root.iconbitmap('data\logo.ico')
        title = "qID - Quick Image Editor | " + appversion
        self.root.title(title)
        self.root.minsize(width=810, height=480)
        self.root.maxsize(width=810, height=480)
        self.statustext = Label(self.root, text = "Please open an image", font=("Century Gothic", 20))
        self.statustext.place(x=250,y=200, anchor='center')
        self.filter_added = False
        self.color_adjust_isapply = False
        self.last_color_adjust = 'none'
        self.count = 1
        self.editlist = [(1,1)] #Edited values for export
        self.brightness_slider_apply_val = 1.0
        self.contrast_slider_apply_val = 1.0
        self.saturation_slider_apply_val = 1.0

        #menubar
        menubar = Menu(self.root)
        self.root.config(menu = menubar)
        fileMenu = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="File", menu = fileMenu)
        fileMenu.add_command(label ="Open image file..", command = self.openfile)

        wMarkMenu = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Watermark", menu = wMarkMenu)
        wMarkMenu.add_command(label ="Select watermark image..", command = self.openwatermarkfile)

        presetMenu = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Preset", menu = presetMenu)
        presetMenu.add_command(label ="Load Preset", command = self.loadpreset)
        presetMenu.add_command(label ="Save current adjustment as Preset", command = self.savepreset)


        helpMenu = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label="Help", menu = helpMenu)
        helpMenu.add_command(label ="About quick Image Develop", command = self.about)




        #Adjustment zone
        color_label = Label(self.root, text = 'Color Adjustment', font=("Century Gothic", 12)).place(x=520, y=30, anchor='w')

        #Brightness

        brightness_label = Label(self.root, text = 'Brightness = ', font=("Century Gothic", 10)).place(x=520, y=60, anchor='w')
        self.bright_slider = tk.Scale(self.root, orient=HORIZONTAL, length = 200 ,from_=0.0, to=2.00,resolution=0.01,showvalue=0,state ='disabled',command=self.update_brightness)
        self.bright_slider.set(1.0)
        self.Brightstatus = Label(self.root, text = "0", font=("Century Gothic", 10))
        self.Brightstatus.place(x = 635, y=47)
        self.bright_slider.place(x = 530, y = 83, anchor = 'w')


        #Contrast
        Label(self.root, text = 'Contrast = ', font=("Century Gothic", 10)).place(x=520, y=120, anchor='w')
        self.contrast_slider = tk.Scale(self.root, orient=HORIZONTAL, length = 200 ,from_=0.0, to=2.00,resolution=0.01,showvalue=0,state ='disabled', command=self.update_contrast)
        self.contrast_slider.set(1.0)
        self.contraststatus = Label(self.root, text = "0", font=("Century Gothic", 10))
        self.contraststatus.place(x = 635, y=107)
        self.contrast_slider.place(x = 530, y = 143, anchor = 'w')

        #Saturation
        Label(self.root, text = 'Saturation = ', font=("Century Gothic", 10)).place(x=520, y=180, anchor='w')
        self.saturation_slider = tk.Scale(self.root, orient=HORIZONTAL, length = 200 ,from_=0.0, to=2.00,resolution=0.01,showvalue=0,state ='disabled', command=self.update_saturation)
        self.saturation_slider.set(1.0)
        self.saturationstatus = Label(self.root, text = "0", font=("Century Gothic", 10))
        self.saturationstatus.place(x = 635, y=167)
        self.saturation_slider.place(x = 530, y = 203, anchor = 'w')

        #applybutton and resetbutton
        self.applybutton = tk.Button(self.root, text="Apply", command = self.applyedit, width=6 ,height = 10,state ='disabled')
        self.applybutton.place(x=740, y = 65)
        self.resetbutton = tk.Button(self.root, text="Reset", command = self.reset, width=6 ,height = 3,anchor='center',state ='disabled')
        self.resetbutton.place(x=740, y = 250)

        #Filter
        self.color_val_var = StringVar()
        Label(self.root, text = 'Instant filter', font=("Century Gothic", 12)).place(x=520, y=240, anchor='w')
        self.color_val = Combobox(self.root, textvariable=self.color_val_var, values = self.colorfilter_list, state = "disabled" )
        self.color_val.bind('<<ComboboxSelected>>', self.filter_add )
        self.color_val.place(x=520, y=270, anchor='w')

        #Export picture width
        self.ex_size = StringVar()
        Label(self.root, text = 'Picture export width', font=("Century Gothic", 12)).place(x=520, y=310, anchor='w')
        self.export_size = Combobox(self.root, textvariable=self.ex_size, values = self.exportwidth, state = "readonly")
        self.export_size.place(x=520, y=340, anchor='w')

        #sharpen for web
        self.sharpenstatus = IntVar()
        Checkbutton(self.root, text="Sharpen for web", variable=self.sharpenstatus).place(x=520, y = 360)

        #watermark
        self.watermarkstatus = IntVar()
        self.wButton  = Checkbutton(self.root, text="Watermark", variable=self.watermarkstatus, state = 'disabled')
        self.wButton.place(x=520, y = 390)


        #exportbutton
       # Button(self.root, text="EXPORT", command = self.saveimg,state ='disabled').place(x=520, y = 420)
        self.exportbutton = tk.Button(self.root, text="EXPORT !", command = self.saveimg, width=10 ,height = 3,anchor='center',state ='disabled')
        self.exportbutton.place(x=708, y = 350)



        self.root.mainloop()


        #VVVVVVVVVV part below are editing mechanism VVVVVVVVVVVVV

    def openwatermarkfile(self):
        self.watermarkfilename = filedialog.askopenfilename(filetypes=(("JPEG Images", "*.jpg"),("ICON Files", "*.ico"),("PNG Files", "*.png"),("All files", "*.*") ))
        if self.watermarkfilename == '':
            return

        try :                                       #Try to check watermark file
            PIL.Image.open(self.watermarkfilename)
            self.wButton["state"] = "normal"
        except:
            messagebox.showerror("Opening File Failed", "Error : Opening watermark image file")

    def openfile(self):
        #basewidth = 500
        print("\n===== Opening Image =====")
        self.statustext["text"] = "Loading..."
        self.filename = tk.filedialog.askopenfilename(filetypes=(("JPEG Images", "*.jpg"),("All files", "*.*") ))

        if self.filename == '':
            self.statustext["text"] = "Please open an image"
            print(" - Cancelled by user.")
            return

        try:                                                                    #Try to check image file is valid or not
            self.image = PIL.Image.open(self.filename)
        except:
            self.statustext["text"] = "Please open an image"
            messagebox.showerror("Opening File Failed", "Error while opening this file")
            print(" - Opening image failed.")
            return

        self.original = self.image.copy()                                       #copy original image for exporting process

        #Resize image to show propery in GUI
        width,height = self.image.size
        size = 'Picture size = ' + str(width) +' x '+ str(height)
        print(" - Opening image sucess Filename :",self.filename,"\n -",size)
        Label(self.root, text=self.filename[:60]).place(x = 10, y=370)
        Label(self.root, text=size).place(x = 10, y=390)
        self.image.thumbnail((500, 500))

        s = 500
        dummyimg = self.image.copy()
        while dummyimg.size[1] > 340:
            dummyimg.thumbnail((s, s))
            s -= 2

        print(" - Displaying image at resolution : ", dummyimg.size[0],dummyimg.size[1])
        self.image.thumbnail((dummyimg.size[0], dummyimg.size[1]))
        self.image_resized = self.image.copy()                              #copy resized image to use when user want to reset image(backup)
        self.tkim = ImageTk.PhotoImage(image = self.image)                  #Convert to tkinter image object

        self.imagelabel = Label(self.root, image=self.tkim)
        self.imagelabel.place(x=10, y=30)


        self.statustext["text"] = ""
        previewlabel = Label(self.root, text = "Preview  :", font=("Century Gothic", 10))
        previewlabel.place(x = 10, y=5)

        try:                                            #Try to intilize value to default value if not open image for first time
            self.reset()
        except:                                         #Set slider to normal and ready to use
            self.bright_slider["state"] = 'normal'
            self.contrast_slider["state"] = 'normal'
            self.saturation_slider["state"] = 'normal'
            self.applybutton["state"] = 'normal'
            self.resetbutton["state"] = 'normal'
            self.exportbutton["state"] = 'normal'
            self.color_val["state"] = 'readonly'
            self.contrast_slider.set(1.0)
            self.saturation_slider.set(1.0)
            self.bright_slider.set(1.0)


    #Reset image to default
    def reset(self):
        try:
            self.filter_add('NONE')
            self.color_val.set('NONE')
        except:
            pass

        self.image = self.image_resized.copy()                      #Copy resized image
        self.image_edited = self.image                              #reset edited image to fresh new image
        self.tkim = ImageTk.PhotoImage(image = self.image)          #Create new Tkinter image object
        self.imagelabel["image"] = self.tkim                        #Show new image in GUI

        #Reset value to default value
        self.filter_added = False
        self.bright_slider["state"] = 'normal'
        self.contrast_slider["state"] = 'normal'
        self.saturation_slider["state"] = 'normal'
        self.applybutton["state"] = 'normal'
        self.resetbutton["state"] = 'normal'
        self.exportbutton["state"] = 'normal'
        self.color_val["state"] = 'readonly'
        self.contrast_slider.set(1.0)
        self.saturation_slider.set(1.0)
        self.bright_slider.set(1.0)
        self.editlist = [(1,1)]
        self.brightness_slider_apply_val = 1.0
        self.contrast_slider_apply_val = 1.0
        self.saturation_slider_apply_val = 1.0

        print("===== Picture has been reset =====\n")

    #apply b/c/s adjustment and save adjusted value for export
    def applyedit(self):
        self.image = self.image_edited
        self.color_adjust_isapply = True
        self.brightness_slider_apply_val = self.bright_slider.get()
        self.contrast_slider_apply_val = self.contrast_slider.get()
        self.saturation_slider_apply_val = self.saturation_slider.get()
        if self.last_color_adjust == 'brightness':
            print((self.editlist[-1])[0], 'b' ,((self.editlist[-1])[1]) , self.bright_value)
            if ((self.editlist[-1])[0] != 'b') or ((self.editlist[-1])[0] == 'b' and (self.editlist[-1])[1] != self.bright_value) :
                self.editlist.append(('b',self.bright_value))
        if self.last_color_adjust == 'contrast':
            if ((self.editlist[-1])[0] != 'c') or ((self.editlist[-1])[0] == 'c' and (self.editlist[-1])[1] != self.contrast_value):
                self.editlist.append(('c',self.contrast_value))
        if self.last_color_adjust == 'saturation':
            if ((self.editlist[-1])[0] != 's') or ((self.editlist[-1])[0] == 's' and (self.editlist[-1])[1] != self.saturation_value):
                self.editlist.append(('s',self.saturation_value))

        print("\n===== Apply =====")
        print(" - Editlist : ",self.editlist)

    #Update brightness and preview in GUI
    def update_brightness(self, value):
        try:
            if self.filter_added:
                if self.count == 1:
                    messagebox.showinfo("Action error", "Instant filter must set to NONE before using Color Adjustment")
                self.count += 1
                return
            if self.last_color_adjust != 'brightness' and self.color_adjust_isapply == False:
                if self.last_color_adjust == 'contrast':
                    self.contrast_slider.set(self.contrast_slider_apply_val)
                if self.last_color_adjust == 'saturation':
                    self.saturation_slider.set(self.saturation_slider_apply_val)

            self.bright_value = float(format(float(value),".5f"))
            self.enhancer = ImageEnhance.Brightness(self.image)
            self.image_edited = self.enhancer.enhance(self.bright_value)
            self.tkim = ImageTk.PhotoImage(image = self.image_edited)
            print(" >Brightness slider set to \t",self.bright_value)
            self.Brightstatus["text"] = int((self.bright_value - 1) *100)  #Update Current value
            self.imagelabel["image"] = self.tkim
            self.color_adjust_isapply = False
            self.last_color_adjust = 'brightness'
        except :
            return

    #Update contrast and preview in GUI
    def update_contrast(self, value):
        try:
            if self.filter_added:
                if self.count == 1:
                    messagebox.showinfo("Action error", "Instant filter must set to NONE before using Color Adjustment")
                self.count += 1
                return

            if self.last_color_adjust != 'contrast' and self.color_adjust_isapply == False:
                if self.last_color_adjust == 'brightness':
                    self.bright_slider.set(self.brightness_slider_apply_val)
                if self.last_color_adjust == 'saturation':
                    self.saturation_slider.set(self.saturation_slider_apply_val)

            self.contrast_value = float(format(float(value),".5f"))
            self.enhancer = ImageEnhance.Contrast(self.image)
            self.image_edited = self.enhancer.enhance(self.contrast_value)
            self.tkim = ImageTk.PhotoImage(image = self.image_edited)
            print(" >Contrast slider set to      \t",self.contrast_value)
            self.contraststatus["text"] = int((self.contrast_value - 1) *100)  #Update Current value
            self.imagelabel["image"] = self.tkim
            self.color_adjust_isapply = False
            self.last_color_adjust = 'contrast'

        except :
            return

    #Update saturation and preview in GUI
    def update_saturation(self, value):
        try:
            if self.filter_added:
                if self.count == 1:
                    messagebox.showinfo("Action error", "Instant filter must set to NONE before using Color Adjustment")
                self.count += 1
                return

            if self.last_color_adjust != 'saturation' and self.color_adjust_isapply == False:
                if self.last_color_adjust == 'brightness':
                    self.bright_slider.set(self.brightness_slider_apply_val)
                if self.last_color_adjust == 'contrast':
                    self.contrast_slider.set(self.contrast_slider_apply_val)


            self.saturation_value = float(format(float(value),".5f"))
            self.enhancer = ImageEnhance.Color(self.image)
            self.image_edited = self.enhancer.enhance(self.saturation_value)
            self.tkim = ImageTk.PhotoImage(image = self.image_edited)
            print(" >Saturation slider set to \t",self.saturation_value)
            self.saturationstatus["text"] = int((self.saturation_value - 1) *100)  #Update Current value
            self.imagelabel["image"] = self.tkim
            self.color_adjust_isapply = False
            self.last_color_adjust = 'saturation'

        except :
            return

    def loadpreset(self):
        print("\n===== Load Preset =====")

        try:                            #Try to check image in program or not
            self.image_edited
        except:
            print(" - Load preset failed.")
            messagebox.showerror("Can't load preset", "No Picture found. Plese open picture first.")
            return

        filename = filedialog.askopenfilename(filetypes=(("qID Preset", "*.qidp"),("All files", "*.*") ))
        if filename == '':
            return

        try :                                                     #Try to check file
            filename = open(filename, 'rb')
            data =  pickle.load(filename)
        except:
            messagebox.showerror("Load preset failed", "Error loading this preset.")
            print(" - Load Preset file error")
            return
        self.reset()
        filename = str(filename)

        filename = (filename.split("name='",1)[1])[:-2]
        print(" - Load Preset file sucess. Filename : ",filename)
        count = 0
        editlist = data[0]
        filtervalue = data[1]

        for i in editlist:                                                          #Applying preset to current picture
            percent = format(count* 100/len(editlist),'.2f')
            print(" >Progress = ",percent,'%')
            key = i[0]
            value = i[1]
            if key == 'b':
                self.enhancer = ImageEnhance.Brightness(self.image_edited)
                self.image_edited = self.enhancer.enhance(value)
                print("- Updated :",key," Value :",value)
            if key == 'c':
                self.enhancer = ImageEnhance.Contrast(self.image_edited)
                self.image_edited = self.enhancer.enhance(value)
                print("- Updated :",key," Value :",value)
            if key == 's':
                self.enhancer = ImageEnhance.Color(self.image_edited)
                self.image_edited = self.enhancer.enhance(value)
                print("- Updated :",key," Value :",value)
            count += 1
        if filtervalue == '':
            filtervalue = 'NONE'

        self.image = self.image_edited
        self.color_val_var.set(filtervalue)
        self.filter_add(filtervalue)
        self.editlist = editlist
        print(" >Progress = 100.00 % : Applying preset to current picture done!" )

    def savepreset(self):
        if (len(self.editlist) == 1) :
            messagebox.showerror("Save Preset failed", "Please edit picture before save preset ")
            print(" - Save preset failed.")
            return

        data = [self.editlist,self.color_val_var.get(),0,'none',self.sharpenstatus.get()]
        filename = tk.filedialog.asksaveasfile(mode='w',initialdir = "/",title = "Preset save dir",filetypes = (("qID Preset","*.qidp"),("all files","*.*")))
        filename = str(filename)
        filename = (filename.split("name='",1)[1])
        filename = (filename.split("' mode='",1)[0])
        os.remove(filename)
        if filename[-4:] != '.qidp':
            filename = filename + '.qidp'
        filename = open(filename, 'wb')
        pickle.dump(data, filename)
        print("Sucessful save preset at :", filename)


    #Add instant filter and preview in GUI
    def filter_add(self,value):
        self.filter_added = True
        filtervalue = (self.color_val_var.get())
        print(" >Adding filter : ",filtervalue)

        if filtervalue == 'CONTOUR':
            self.image2 = self.image_edited.filter(ImageFilter.CONTOUR)
        if filtervalue == 'DETAIL':
            self.image2 = self.image_edited.filter(ImageFilter.DETAIL)
        if filtervalue == 'BLUR':
            self.image2 = self.image_edited.filter(ImageFilter.BLUR)
        if filtervalue == 'EMBOSS':
            self.image2 = self.image_edited.filter(ImageFilter.EMBOSS)
        if filtervalue == 'SMOOTH':
            self.image2 = self.image_edited.filter(ImageFilter.SMOOTH)
        if filtervalue == 'NONE':
            self.image2 = self.image_edited.copy()
            self.filter_added = False
            self.count = 1                                                  #filter changing count

        self.tkim_edit = ImageTk.PhotoImage(image = self.image2)            #convert image object to Tkinter image
        self.imagelabel["image"] = self.tkim_edit                           #show(preview) edited in gui

        if self.count == 1 and self.filter_added:                           #Display warning for first time that user add filter
            messagebox.showinfo("Warning...", "Color Adjustment are disabled.\n Set filter back to NONE to use Color Adjustment again.")
            self.count += 1

        if self.filter_added:                                               #Disable Color adjustment after adding filter
            self.bright_slider["state"] = 'disabled'
            self.contrast_slider["state"] = 'disabled'
            self.saturation_slider["state"] = 'disabled'
        else:
            self.bright_slider["state"] = 'normal'
            self.contrast_slider["state"] = 'normal'
            self.saturation_slider["state"] = 'normal'

    #about program popup page
    def about(self):
        info = "  qID | Quick Image Develop - Version " + appversion + "\n\n  Software by Sitinut Waisara @Software Engineer IC,KMITL\
                            \n\n  Do not modified, re-distributed without the author's permission\n\n \
                            \n  copyright ©2016 PRO4+ Studio all rights reserved"
        messagebox.showinfo("About qID", info)

    #export image
    def saveimg(self):
        self.export = self.original.copy() #copy original image to exporting image
        size = 0            #size 0 = No need to resize

        #check size combobox if user change value or not
        try:
            size = int(self.export_size.get()[:-2])
        except:
            pass

        #check user imported watermark or not
        try:
            self.watermarkfilename
        except:
            self.watermarkfilename = 'none'
            

        self.applyedit()

        process(self.export,self.editlist,self.color_val_var.get(),self.watermarkstatus.get(),self.watermarkfilename,size,self.sharpenstatus.get())
        


MainApp()
