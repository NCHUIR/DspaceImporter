#!/usr/bin/python

import os,sys
from tkinter import *
from tkinter.filedialog import askdirectory

sys.path.append('OldFormatToCsv/')
from OldFormatToCsv import OldFormatToCsv

sys.path.append('csvToDspaceSaf/')
from csvToDspaceSaf import csvToDspaceSaf

sys.path.append('safSshDspace/')
from safSshDspace import safSshDspace

setting = {
    'AddButtonText':["新增 NTUR 格式","新增 CSV 格式","選定包含 SAF 資料夾"],
    'goButtonText':['轉換為 CSV 格式','轉換為 SAF 格式','上傳至 Dspace'],

    'OldFormatReqiredExt':[['xls','xlsx']],
    'OldFormatFilteredExt':['csv'],
}

def multiLevelSniff(dirpath,requiredExt,filteredExt = []):
    passedPath = []
    for walker in os.walk(dirpath):
        requiredExtTmp = requiredExt[:]
        require = len(requiredExtTmp)
        for f in walker[2]:
            ext = os.path.splitext(f)[1].lower().replace('.','')
            if ext:
                for i in range(require):
                    if ext in requiredExtTmp[i]:
                        requiredExtTmp.pop(i)
                        require -= 1
                        break
                if ext in filteredExt:
                    require = -1
                    continue
        if require is 0:
            passedPath.append(walker[0])

    return passedPath

class Redir(object):
    # This is what we're using for the redirect, it needs a text box
    def __init__(self, textbox):
        self.textbox = textbox
        self.textbox.config(state=NORMAL)
        self.fileno = sys.stdout.fileno

    def write(self, message):
        # When you set this up as redirect it needs a write method as the
        # stdin/out will be looking to write to somewhere!
        self.textbox.insert(END, str(message))
        self.textbox.see(END)

dirs = [[],[],[]]

def addDir(i):
    dirpath = askdirectory()
    if dirpath:
        print("directory chosen:",dirpath)


        paths = multiLevelSniff(dirpath,setting['OldFormatReqiredExt'],setting['OldFormatFilteredExt'])
        print("paths:",paths)

        for path in paths:
            
            item = {'dir':os.path.split(path)[1],'path':path}
            dirs.append(item)
            listbox[i].insert(END,item['dir'])


root = None
frame = []
ctrlFrame = None
add_button = []
go_button = []
listbox = []
ctrlButton = None

def buildGUI():

    # Make the root window
    root = Tk()

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    addDirMap = [lambda : addDir(0),lambda : addDir(1),lambda : addDir(2)]

    listsFrame = Frame(root)
    listsFrame.pack(side='top',fill=BOTH,expand=1)
    for x in range(3):
        frameTmp = Frame(listsFrame)
        frameTmp.pack(side='left',expand=1,fill=BOTH,padx=10)
        frame.append(frameTmp)

        buttonTmp = Button(frameTmp,text=setting['AddButtonText'][x],command=addDirMap[x])
        buttonTmp.pack(side = 'top')
        add_button.append(buttonTmp)

        listboxTmp = Listbox(frameTmp,relief='ridge')
        listboxTmp.pack(side = 'top',fill=BOTH,expand=1)
        listbox.append(listboxTmp)

        buttonTmp = Button(frameTmp,text=setting['goButtonText'][x])
        buttonTmp.pack(side = 'top')
        add_button.append(buttonTmp)



    ctrlFrame = Frame(root)
    ctrlFrame.pack(side='bottom',fill='x')

    consoleFrame = Frame(ctrlFrame)
    consoleFrame.pack(side='top',fill=BOTH)

    ctrlButton = Button(ctrlFrame,text='轉換至 SAF 並上傳')
    ctrlButton.pack(side='top', fill='x')

    # lb=Text(root, width=16, height=5, font=dFont)
    # yscrollbar=Scrollbar(root, orient=VERTICAL, command=lb.yview)
    # yscrollbar.pack(side=RIGHT, fill=Y)
    # lb["yscrollcommand"]=yscrollbar.set
    # lb.pack(side=LEFT, fill=BOTH, expand = YES)

    console = Text(consoleFrame,height=10, wrap=WORD,state=DISABLED,takefocus=0,relief=FLAT,bg="black",fg="#4E8D82",highlightthickness=0)

    consoleScrollbar = Scrollbar(consoleFrame, orient=VERTICAL)
    consoleScrollbar.pack(side=RIGHT, fill=Y)
    consoleScrollbar.config(command=console.yview)

    console['yscrollcommand'] = consoleScrollbar.set

    console.pack(side=LEFT, fill=BOTH, expand = YES)

    
    # font=("Helvetica",13),
    # state=DISABLED, 
    # Set up the redirect 
    stdre = Redir(console)
    # Redirect stdout, stdout is where the standard messages are ouput
    sys.stdout = stdre
    # Redirect stderr, stderr is where the errors are printed too!
    sys.stderr = stdre

    # console.grid(row=0,column=0,sticky=N+S+W+E)

    # scrollbar.config(command=console.yview)

    # for r in range(3):
    #     for c in range(4):
    #         Label(root, text='R%s/C%s'%(r,c),
    #             borderwidth=1 ).grid(row=r,column=c)
    # root.mainloop(  )

    root.minsize(400, 400)

    # oldFormatAddButton = Button(root, text = '新增舊格式')

    # # Make a button to get the file name
    # # The method the button executes is the askopenfilename from above
    # # You don't use askopenfilename() because you only want to bind the button
    # # to the function, then the button calls the function.
    # button = Button(root, text='GetFileName', command=addDir)
    # # this puts the button at the top in the middle
    # button.grid(row=1, column=1)

    # # Make a scroll bar so we can follow the text if it goes off a single box
    # scrollbar = Scrollbar(root, orient=VERTICAL)
    # # This puts the scrollbar on the right handside
    # scrollbar.grid(row=2, column=3, sticky=N+S+E)

    # # Make a text box to hold the text
    # textbox = Text(root,font=("Helvetica",20),state=DISABLED, yscrollcommand=scrollbar.set, wrap=WORD)
    # # This puts the text box on the left hand side
    # textbox.grid(row=2, column=0, columnspan=3, sticky=N+S+W+E)

    # # Configure the scroll bar to stroll with the text box!
    # scrollbar.config(command=textbox.yview)

    # Print hello so we can see the redirect is working!
    print("hello")

    # # Start the application mainloop
    root.mainloop()

if __name__ == '__main__':
    buildGUI()
    # print("multiLevelSniff:",multiLevelSniff(sys.argv[1],[['xls','xlsx'],['pdf']],['csv']))
