import tkinter as tk
import os
from tkinter import filedialog, messagebox

class MainWindow():
    def __init__(self):
        self.tw = tk.Tk()
        self.tw.geometry("400x300")
        self.tw.title('csv2vcd - by feecat')

        self.sourcefile=''
        self.outputfile=''
        self.seperator=','
        self.triggervoltage=1.8

        my_font1=('times', 18, 'bold')
        self.l1 = tk.Label(self.tw,text='Picoscope csv to Pulseview vcd',width=30,font=my_font1).pack()

        self.b1 = tk.Button(self.tw, text='Select File', width=20,command = self.select_file).pack()
        self.sourcefilevar = tk.StringVar()
        self.sourcefilevar.set("Please Select Source file.")
        self.w1 = tk.Label(self.tw, textvariable=self.sourcefilevar).pack()     

        self.b2 = tk.Button(self.tw, text='Select Output', width=20,command = self.save_file).pack()
        self.outputfilevar = tk.StringVar()
        self.outputfilevar.set("Please Select Output file.")
        self.w2 = tk.Label(self.tw, textvariable=self.outputfilevar).pack()

        self.b4 = tk.Button(self.tw, text='change seperator , or ;', width=20,command = self.change_separator).pack()
        self.seperatorvar = tk.StringVar()
        self.seperatorvar.set("Seperator is: " + self.seperator)
        self.w4 = tk.Label(self.tw, textvariable=self.seperatorvar).pack()

        self.b3 = tk.Button(self.tw, text='Start Converter', width=20,command = self.start_converter).pack()
        self.resultvar = tk.StringVar()
        self.resultvar.set("Waiting Select File.")
        self.w3 = tk.Label(self.tw, textvariable=self.resultvar).pack()
        self.tw.mainloop()

    def change_separator(self):
        if self.seperator == ",":
            self.seperator = ';'
        else:
            self.seperator = ','
        self.seperatorvar.set("Seperator is: " + self.seperator)
        
    def check_dir(self):
        if len(self.sourcefile) > 0 and len(self.outputfile) > 0:
            self.resultvar.set("Waiting Start Converter")
    
    def select_file(self):
        self.sourcefile = filedialog.askopenfilename(filetypes=[("PicoScope CSV",".csv")])
        self.outputfilevar.set('Source File: ')
        if len(self.sourcefile) > 0:
            self.sourcefilevar.set('Source File: ' + self.sourcefile)

            self.outputfile = self.sourcefile[:len(self.sourcefile)-3] + 'vcd'
            self.outputfilevar.set('Output File: ' + self.outputfile)
            self.check_dir()
        
    def save_file(self):
        self.outputselect = filedialog.asksaveasfile(initialfile=self.outputfile, filetypes=[("PulseView VCD",".vcd")])
        if hasattr(self.outputselect,'name'):
            self.outputfile = self.outputselect.name
            self.outputfilevar.set('Output File: ' + self.outputfile)
            self.check_dir()
    
    def start_converter(self):
        print('sourcefile:',self.sourcefile)
        print('savefile:',self.outputfile)
        if len(self.sourcefile) > 0 and len(self.outputfile) > 0:
            self.resultvar.set("In Processing...")
            self.tw.update()
            try:
                fo = open(self.sourcefile, mode='r', encoding='UTF-8')
                fw = open(self.outputfile, mode='w')
                dataline = fo.readline()#first line, Multi language, we dont use it
                dataline = fo.readline()#second line, we got timebase (ns, us, ms, s, min)
                base = ['ns','us','ms','s']
                time = dataline.split(self.seperator)[0][1:-1]
                for i in range(len(base)):
                    if time == base[i]:
                        multi = 1000 ** i
                dataline = fo.readline()#empty line

                dataline = fo.readline()#first data line
                dataline = dataline.replace(",", "." )#replace , with
                print('dataline:',dataline)
                channel = dataline.count(self.seperator)
                timebase = dataline.split(self.seperator)[0]
                data = dataline.split(self.seperator)
                data[channel]=data[channel][:len(data[channel])-1] #remove \n
                for i in range(channel):
                    data[i+1] = data[i+1] if len(data[i+1]) > 2 else '0'
                string = '#' + str(round((float(data[0])-float(timebase))*multi)) + ' r' + data[1] + ' % '
                if channel == 1:
                    string = string + '\n'
                elif channel == 2:
                    string = string + 'r' + data[2] + ' & ' + '\n'
                
                fw.writelines('$timescale 1 ns $end\n')
                fw.writelines('$scope module libsigrok $end\n')
                fw.writelines('$var real 64 % A0 $end\n')
                if channel > 1:
                    fw.writelines('$var real 64 & A1 $end\n')
                fw.writelines('$upscope $end\n')
                fw.writelines('$enddefinitions $end\n')
                fw.writelines(string)

                linenum = 4
                for line in fo:
                    line = line.replace(",", "." )#replace , with
                    print('line:',line)
                    linenum = linenum + 1
                    data = line.split(self.seperator)
                    data[channel]=data[channel][:len(data[channel])-1] #remove \n
                    if linenum == 5:
                        factor = str(round((float(data[0])-float(timebase))*multi))
                    for i in range(channel):
                        data[i+1] = data[i+1] if len(data[i+1]) > 2 else '0'
                    string = '#' + str(round((float(data[0])-float(timebase))*multi)) + ' r' + data[1] + ' % '
                    if channel == 1:
                        string = string + '\n'
                    elif channel == 2:
                        string = string + 'r' + data[2] + ' & ' + '\n'
                    fw.writelines(string)
                fo.close()
                fw.close()
                result = 'Converter Finished!' + '\n' + 'Line:' + str(linenum) + '\n' + 'Suggest Downsampling Factor:' + factor
                self.resultvar.set(result)
            except Exception as e:
                messagebox.showerror(title='Error!', message=e)
                self.resultvar.set("Converter Failed!")
        else:
            messagebox.showwarning(title='Warning!', message='No file selected!')

if __name__ == "__main__":
    app = MainWindow()