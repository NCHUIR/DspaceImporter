#!/usr/bin/python

import os,sys,json,re
from tkinter import *
from threading import Thread
from tkinter.filedialog import askdirectory

sys.path.append('OldFormatToCsv/')
from OldFormatToCsv import OldFormatToCsv

sys.path.append('csvToDspaceSaf/')
from csvToDspaceSaf import csvToDspaceSaf

sys.path.append('safSshDspace/')
from safSshDspace import safSshDspace

setting = {
    "safSshDspace":{
        "hostname":"",
        "username":"",
        "password":"",

        "SAFTmpDir":"",

        "requireRoot":"False",
        "dspaceBin":"",
        "mapfileDir":"",
        "DspaceIdentity":""
    },
    "OldFormatToCsv":{},
    "csvToDspaceSaf":{},

    'AddButtonText':["新增 NTUR 格式","新增 CSV 格式","新增 SAF 格式"],
    'goButtonText':[
        ['轉換為 CSV 格式','清除所選'],
        ['轉換為 SAF 格式','清除所選'],
        ['上傳至 Dspace','清除所選']
    ],
    'typeName':['NTUR (舊格式)','CSV 格式','SAF 格式'],

    'ctrlButtonText':['自動轉換至 SAF 並上傳','停止'],

    'OldFormatReqiredExt':[['xls','xlsx'],['pdf']],
    'OldFormatFilteredExt':['csv'],

    'csvRequiredExt':[['csv'],['pdf']],
    'csvFilteredExt':[],

    'csvName':False,

    'askSafLocationPrompt':'請選擇 SAF 格式放置位置',

    'HandlePrefix':'123456789',

    'SAFCollFolderRegex':r'^.+\[(\d+)\]$', # Group $1 is the handle (digits after '/')
    'HandleRegex':r'\d+',

    'HandlePrompt':'請問要傳到哪個 Handle? (輸入斜線之後的數字即可)',

    'askJsonDirPrompt':'請選擇 mapfile 之 json 格式之存放位置',

    'askDirFallback':'./'
}

class InputDialog(object):
    def __init__(self,master,text="",buttonText=""):
        top=self.top=Toplevel(master)
        self.l=Label(top,text=text)
        self.l.pack()
        self.e=Entry(top)
        self.e.pack()
        self.b=Button(top,text=buttonText,command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()

def askInput(text="",buttonText=""):
    global root
    w=InputDialog(root,text,buttonText)
    root.wait_window(w.top)
    return w.value

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

def findExt(dirpath,ext):
    for f in os.listdir(dirpath):
        # print(">> [%s]" % os.path.splitext( os.path.basename( f ))[1].replace('.','').lower())
        # print("<< [%s]" % ext)
        # print("??",os.path.splitext( os.path.basename( f ))[1].replace('.','').lower() == ext)
        if os.path.splitext( os.path.basename( f ))[1].replace('.','').lower() == ext:
            return os.path.join(dirpath,f)

def previusDir(dirpath): # get previous directive,ex: /var/www => /var/
    return os.path.abspath(os.path.join(dirpath, os.pardir))

def loadJsonConfig(jsonPath):
    jsonFile=open(jsonPath)
    data = json.load(jsonFile)
    jsonFile.close()
    return data

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
safOutputPath = False
jsonOutputPath = False
SafRe = re.compile(setting['SAFCollFolderRegex'])
handleRe = re.compile(setting['HandleRegex'])

def getHandle(dirName,dirpath):
    global SafRe,handleRe
    SafMatch = SafRe.match(dirName)
    if SafMatch:
        handle = SafMatch.group(1)
    else:
        handle = askInput(('[%s]: ' % dirName)+ setting['HandlePrompt'],"OK")
        while not handleRe.match(handle):
            handle = askInput(setting['HandlePrompt'],"OK")

    return setting['HandlePrefix'] + '/' + handle


def getSafPath():
    global safOutputPath
    if not safOutputPath:
        safOutputPath = askdirectory(title=setting['askSafLocationPrompt'])
        if not safOutputPath:
            print("Warning: You didnt choose a directory! Use fallback:[%s]" % setting['askDirFallback'])
            safOutputPath = setting['askDirFallback']
        print("================================================")
        print("\tSAF output folder set:",safOutputPath)
        print("================================================")

    return safOutputPath

def getJsonOutputPath():
    global jsonOutputPath
    if not jsonOutputPath:
        jsonOutputPath = askdirectory(title=setting['askJsonDirPrompt'])
        if not jsonOutputPath:
            print("Warning: You didnt choose a directory! Use fallback:[%s]" % setting['askDirFallback'])
            jsonOutputPath = setting['askDirFallback']
        print("================================================")
        print("\tMapJson output folder set:",safOutputPath)
        print("================================================")

    return jsonOutputPath

def addToDirList(i,path):
    dirName = os.path.split(path)[1]

    if path in [d['path'] for d in dirs[i]]:
        print("dirName:[%s] >> Its path was added already... skipped" % dirName)
        return

    if i is 1:
        item = {'dir':dirName,'path':findExt(path,'csv')}
    elif i is 2:
        item = {'dir':dirName,'path':path,'handle':getHandle(dirName,path)}
    else:
        item = {'dir':dirName,'path':path}

    item['isDone'] = False

    print("Adding dir:[%s] into %s list..." % (item['dir'],setting['typeName'][i]))
    dirs[i].append(item)
    listbox[i].insert(END,item['dir'])

def addDir(i):
    dirpath = askdirectory()
    if dirpath:
        print("directory chosen:",dirpath)

        if i is 0:
            paths = multiLevelSniff(dirpath,setting['OldFormatReqiredExt'],setting['OldFormatFilteredExt'])
        elif i is 1:
            paths = multiLevelSniff(dirpath,setting['csvRequiredExt'],setting['csvFilteredExt'])
        elif i is 2:
            paths = model[2].genSAFList(dirpath)

        print("availible paths detected:",paths)

        for path in paths:
            addToDirList(i,path)

def setAction(i,actCode):
    global go_button
    go_action[i]=actCode
    go_button[i].config(text=setting['goButtonText'][i][actCode])

def onselect(i):
    global listbox
    # Note here that Tkinter passes an event object to onselect()
    w = listbox[i]
    s = w.curselection()

    if len(s):
        setAction(i,1)
    else:
        setAction(i,0)

def doneItem(i,index,isSuccess):
    global listbox
    if isSuccess:
        bg = 'green'
    else:
        bg = 'red'
    dirs[i][index]['isDone'] = isSuccess
    dirs[i][index]['isSuccess'] = isSuccess
    listbox[i].itemconfig(index,background=bg)

def buttonsCtrl(toEnable):
    if toEnable:
        state = NORMAL
        ctrlIndex = 0
    else:
        state = DISABLED
        ctrlIndex = 1

    for i in range(3):
        add_button[i].config(state = state)
        go_button[i].config(state = state)
    ctrlButton.config(text = setting['ctrlButtonText'][ctrlIndex])

go_action = [0,0,0]
keepGoing = False

def go(i):
    def raiseErrInProc(i):
        raise Exception("There is some ERROR in Process [%s]! Please check logs in console..." % setting['typeName'][i])

    global listbox,keepGoing,running,go_action
    if go_action[i]:
        indexes = [int(j) for j in listbox[i].curselection()]
        indexes.sort()
        shift = 0
        for j in indexes:
            print("[%s] removed." % dirs[i].pop(j-shift)['dir'])
            listbox[i].delete(j-shift)
            shift += 1
        setAction(i,0)
    else:
        sshConnected = False
        buttonsCtrl(False)
        keepGoing = True
        running = True
        errs = []
        for j in range(len(dirs[i])):
            d = dirs[i][j]
            if d['isDone']:
                continue

            if not keepGoing:
                running = False
                print("<<< Process Terminated by User >>>")
                break

            try:
                print("==========[%s]:[%s]==========" % (setting['typeName'][i],d['dir']))

                if i is 0:
                    r = model[0].convert(d['path'],setting['csvName'])

                    if type(r) is Exception:
                        errs.append({'dirName':d['dir'],'err':r})
                        raiseErrInProc(i)

                    addToDirList(1,d['path'])
                elif i is 1:
                    r = model[1].main(d['path'],getSafPath())

                    if len(r) is not 0:
                        errs += [{'dirName':d['dir'],'err':e} for e in r]
                        raiseErrInProc(i)

                    addToDirList(2,os.path.join(getSafPath(),d['dir']))
                elif i is 2:

                    try:
                        if not sshConnected:
                            model[2].connect()
                            sshConnected = True
                        model[2].importOneSaf(d['path'],d['handle'],getJsonOutputPath())
                    except Exception as e:
                        errs.append({'dirName':d['dir'],'err':e})
                        raiseErrInProc(i)
                doneItem(i,j,True)
            except Exception as e:
                print("ERROR:\n\t",e)
                doneItem(i,j,False)
        if sshConnected:
            model[2].client.close()

        print("================================================")
        print("\tProcess Done!!")
        print("================================================")

        if len(errs):
            print("<<<<< There is some ERROR !!! >>>>>")

        for e in errs:
            print("\n==== Exception in process %s [%s] ==========" % (setting['typeName'][i],e['dirName']))
            print( e['err'] )

        buttonsCtrl(True)
        keepGoing = False
        running = False

running = False

def ctrlPress():
    global running,keepGoing
    if running:
        print("================================================")
        print("\tPrepare to be terminated!!")
        print("================================================")
        keepGoing = False
    else:
        getSafPath()
        getJsonOutputPath()
        for i in range(3):
            go(i)

root = None
add_button = []
go_button = []
listbox = []
ctrlButton = None


def buildGUI():

    # Make the root window
    global root,listbox,add_button,go_button,ctrlButton
    root = Tk("DspaceImporter")

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    addDirMap = [
        lambda : Thread(target=addDir,args=(0,)).start(),
        lambda : Thread(target=addDir,args=(1,)).start(),
        lambda : Thread(target=addDir,args=(2,)).start()
    ]
    onselectMap = [lambda e : onselect(0),lambda e : onselect(1),lambda e : onselect(2)]
    goMap = [
        lambda : Thread(target=go,args=(0,)).start(),
        lambda : Thread(target=go,args=(1,)).start(),
        lambda : Thread(target=go,args=(2,)).start()
    ]

    listsFrame = Frame(root)
    listsFrame.pack(side='top',fill=BOTH,expand=1)
    for x in range(3):
        frameTmp = Frame(listsFrame)
        frameTmp.pack(side='left',expand=1,fill=BOTH,padx=10)

        buttonTmp = Button(frameTmp,text=setting['AddButtonText'][x],command = addDirMap[x])
        buttonTmp.pack(side = 'top')
        add_button.append(buttonTmp)

        listboxTmp = Listbox(frameTmp,relief='ridge',selectmode='multiple')
        listboxTmp.pack(side = 'top',fill=BOTH,expand=1)

        listboxTmp.bind('<<ListboxSelect>>', onselectMap[x])

        listbox.append(listboxTmp)

        buttonTmp = Button(frameTmp,text=setting['goButtonText'][x][0],command = goMap[x])
        buttonTmp.pack(side = 'top')
        go_button.append(buttonTmp)

    ctrlFrame = Frame(root)
    ctrlFrame.pack(side='bottom',fill='x')

    consoleFrame = Frame(ctrlFrame)
    consoleFrame.pack(side='top',fill=BOTH)

    ctrlButton = Button(ctrlFrame,text=setting['ctrlButtonText'][0],
        command = lambda : Thread(target=ctrlPress).start()
    )
    ctrlButton.pack(side='top')

    console = Text(consoleFrame,height=10, wrap=WORD,state=DISABLED,takefocus=0,relief=FLAT,bg="black",fg="#4E8D82",highlightthickness=0)

    consoleScrollbar = Scrollbar(consoleFrame, orient=VERTICAL)
    consoleScrollbar.pack(side=RIGHT, fill=Y)
    consoleScrollbar.config(command=console.yview)

    console['yscrollcommand'] = consoleScrollbar.set

    console.pack(side=LEFT, fill=BOTH, expand = YES)

    stdre = Redir(console)
    sys.stdout = stdre
    sys.stderr = stdre

    root.minsize(400, 400)

    print("hello")

    root.mainloop()

model = None

if __name__ == '__main__':

    setting.update(loadJsonConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)),'setting.json')))

    model = [
        OldFormatToCsv(setting['OldFormatToCsv']),
        csvToDspaceSaf(setting['csvToDspaceSaf']),
        safSshDspace(setting['safSshDspace'])]

    buildGUI()
