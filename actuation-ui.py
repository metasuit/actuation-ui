import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import signal
import random
import time
import serial



class actuationUI(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        #Configure root tk class
        self.master = master
        self.master.title("Actuation UI")
        self.master.iconbitmap("assets/metasuit.ico")
        self.master.geometry("1100x600")

        


        self.create_widgets()
        self.pack()
        self.run = False

        #Configure Arduino connection
        self.arduino = serial.Serial(port='COM6' , baudrate=115200, timeout=.1)
        self.bufferSize = 3
        #write error message if port could not be opened 


        self.initialSignal()

        # self.amplitude = self.automaticActuationFrame.sliderAmplitude.get()
        # self.freq = self.automaticActuationFrame.sliderFreq.get()

        
        # self.y = np.zeros(len(self.t))
        # self.y_neg =  np.zeros(len(self.t_neg))

        # self.signal = np.append(self.y_neg, self.y)

        self.unelegant_count = 0

        self.updateGraph()


    def create_widgets(self):

        #The main frame is made up of three subframes
        self.channelSettingsFrame = channelSettings(self, title ="Channel Settings")
        self.channelSettingsFrame.grid(row=0, column=1, sticky="ew", pady=(20,0), padx=(20,20), ipady=10)

        self.automaticActuationFrame = automaticActuation(self, title="Automatic Actuation")
        self.automaticActuationFrame.grid(row=1, column=1, pady=(20,0), padx=(20,20), ipady=10)

        self.graphDataFrame = graphData(self)
        self.graphDataFrame.grid(row=0, rowspan=2, column=2, pady=(20,0), ipady=10)


    def startTask(self):
        #Prevent user from starting task a second time
        self.automaticActuationFrame.startButton['state'] = 'disabled'
        self.automaticActuationFrame.sliderFreq['state'] = 'disabled'
        self.automaticActuationFrame.actuationTypeMenu['state'] = 'disabled'

        #Shared flag to alert task if it should stop
        self.continueRunning = True

        #spin off call to check 
        if(self.mode == "Manual"):
            self.master.after(100, self.runManualTask)

        else:
            self.master.after(100, self.runTask)
            self.automaticActuationFrame.sliderAmplitude['state'] = 'disabled'

        print(self.arduino)

        self.start_time = time.time()


    def runTask(self):
        #Check if task needs to update the graph


        #This cuts the 0 signal from the user interface
        if(self.unelegant_count == self.multiple*200):
            self.signal = self.signal[:-int(self.multiple*200)]
            self.time = self.time[:-int(self.multiple*200)]
        elif(self.unelegant_count == 2*self.multiple*200):
            self.unelegant_count = self.multiple*200 + 1
        
        #This needs to be updated for correct time
        self.signal = np.roll(self.signal, -1)

        # This is the frequency of updating thte graph (lower for saving computer power)
        if(self.unelegant_count %250 == 0):
            self.updateGraph()

        self.unelegant_count += 1

        # This signal is the signal at time = 0 and should be sent to the arduino board
        print(self.signal[int(self.multiple*200)])

        #check if the task should sleep or stop
        if(self.continueRunning):
            self.master.after(2, self.runTask)
       

    def runManualTask(self):
        self.amplitude = str(self.automaticActuationFrame.getCurrentValueAmplitude())
        print(self.amplitude)
        # self.arduino.write(bytes(self.amplitude,'utf-8'))
        # time.sleep(0.05)
         # Convert data to bytes and add padding if necessary
        self.amplitude = str(self.amplitude).zfill(self.bufferSize).encode()
        # Send data to Arduino
        self.arduino.write(self.amplitude)
        # Wait for a moment to ensure the data is sent
        time.sleep(0.01)

    
        # self.signal[int(self.multiple*200)] = self.amplitude
        # print(self.signal[int(self.multiple*200)])


        # self.signal = np.roll(self.signal, -1)

        # self.unelegant_count += 1 
        # print(self.unelegant_count)


        # if(self.unelegant_count %50 == 0):
        #     self.updateGraph()
        #     self.unelegant_count = 0

        if(self.continueRunning):
            self.master.after(2, self.runManualTask)



    def stopTask(self):
        #call back for the "stop task" button
        self.continueRunning = False
        self.automaticActuationFrame.startButton['state'] = 'enabled'
        self.automaticActuationFrame.sliderFreq['state'] = 'enabled'
        self.automaticActuationFrame.actuationTypeMenu['state'] = 'enabled'
        self.automaticActuationFrame.sliderAmplitude['state'] = 'enabled'
        self.unelegant_count = 0
        self.initialSignal()
        self.createSignal()

        
    def initialSignal(self):
        self.current_line = np.linspace(0,255, 5)

        self.t = np.linspace(0,6, 1200)
        self.t_neg = np.linspace(-1,0, 200, endpoint=False)
        self.time = np.append(self.t_neg, self.t)

        self.y = np.zeros(len(self.t))
        self.y_neg =  np.zeros(len(self.t_neg))

        self.createSignal()

    def createSignal(self):
        self.amplitude = float(self.automaticActuationFrame.getCurrentValueAmplitude())
        self.period = float(self.automaticActuationFrame.getCurrentValueFreq())
        
        self.freq = 1/self.period

        self.multiple = self.smallest_multiple_greater_than_6()

        self.mode = self.automaticActuationFrame.optionActVar.get() 

        self.t_neg = np.arange(-1,0, 1/(self.multiple*200))
        self.t_neg = np.delete(self.t_neg, -1)
        self.t = np.arange(0, self.multiple, 1/(self.multiple*200))
        
        if(self.mode == "Manual"):
            self.automaticActuationFrame.sliderFreq['state'] = 'disabled'
            self.y =  np.zeros(len(self.t))

           
           
        elif(self.mode == "Step"):
            self.automaticActuationFrame.sliderFreq['state'] = 'disabled'
            self.y =  self.amplitude*np.ones(len(self.t))
        elif(self.mode == "Sine"):
            self.automaticActuationFrame.sliderFreq['state'] = 'enabled'
            
            self.y =  self.amplitude/2 - self.amplitude/2*np.cos(2*np.pi*self.freq*self.t)
        elif(self.mode == "Square"):
            self.automaticActuationFrame.sliderFreq['state'] = 'enabled'
            self.y =  0.5*(self.amplitude + self.amplitude*signal.square(2*np.pi*self.freq*self.t))
        elif(self.mode == "Triangle"):
            self.automaticActuationFrame.sliderFreq['state'] = 'enabled'
            self.y =  self.amplitude*0.5*(1 + signal.sawtooth(2 * np.pi * self.freq * self.t, 0.5))
        elif(self.mode == "Sawtooth"):
            self.automaticActuationFrame.sliderFreq['state'] = 'enabled'
            self.y =  self.amplitude/2*(1+signal.sawtooth(2 * np.pi * self.freq * self.t))
        else:
            print("Error: Invalid actuation type") 
            return None
        
        self.y_neg =  np.zeros(len(self.t_neg))

        self.signal = np.append(self.y_neg, self.y)
        self.time = np.append(self.t_neg, self.t)

        self.updateGraph()

    def updateGraph(self):
        #Update the graph with the current values
        #make a match statement
        
        self.graphDataFrame.ax.cla()
        self.graphDataFrame.ax.set_ylim(0, 255)
        self.graphDataFrame.ax.set_xlim(-1, 5)
        self.graphDataFrame.ax.set_xlabel("Time (s)   t = 0: current time")
        self.graphDataFrame.ax.set_ylabel("Duty Cycle")
        self.graphDataFrame.ax.set_title("Voltage Input")
        self.graphDataFrame.ax.plot(self.time,self.signal, color='b')
        self.graphDataFrame.ax.axvline(x=0, color='r')
        self.graphDataFrame.ax.axvline(x=self.period, color='r')
        self.graphDataFrame.graph.draw()


    def smallest_multiple_greater_than_6(self):
        self.multiple = self.period
        while self.multiple <= 6:
            self.multiple += self.period
        return self.multiple




class channelSettings(tk.LabelFrame):

    def __init__(self, parent, title):
        tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        self.parent = parent

        self.boardTypes = ["UNO", "MEGA"]
        self.optionBoardVar = tk.StringVar(self)


        self.channelPorts = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"]
        self.optionPortVar = tk.StringVar(self)


        self.grid_columnconfigure(0, weight=1)
        self.xPadding = (30,30)
        self.create_widgets()

    def create_widgets(self):

        self.boardTypeLabel = ttk.Label(self, text="Board Type")
        self.boardTypeLabel.grid(row=0,sticky='w', padx=self.xPadding, pady=(10,0))

        self.boardTypeMenu = ttk.OptionMenu(
            self,
            self.optionBoardVar,
            self.boardTypes[0],
            *self.boardTypes)
        self.boardTypeMenu.grid(row=1, sticky="ew", padx=self.xPadding)

        self.channelPortLabel = ttk.Label(self, text="Arduino USB Port")
        self.channelPortLabel.grid(row=2,sticky='w', padx=self.xPadding, pady=(10,0))

        self.channelPortMenu = ttk.OptionMenu(
            self,
            self.optionPortVar,
            self.channelPorts[0],
            *self.channelPorts)
        self.channelPortMenu.grid(row=3, sticky="ew", padx=self.xPadding)

    def boardTypeChanged(self,event):
        self.parent.arduino = self.optionBoardVar.get()




class automaticActuation(tk.LabelFrame):

    def __init__(self, parent, title):
        tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        self.parent = parent

        self.actuationTypes = ["Manual", "Step","Square", "Sine", "Triangle", "Sawtooth"]
        self.optionActVar = tk.StringVar(self)

        self.xPadding = (30,30)
        self.create_widgets()

    def create_widgets(self):
  

        self.sliderAmplitudeLabel = ttk.Label(self, text="Duty Cylce [0,255]")
        self.sliderAmplitudeLabel.grid(row=0, column=1, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))

        self.maxAmplitudeCurrentValue = tk.DoubleVar()
        self.currentValueAmplitudeLabel = ttk.Label(self, text=self.getCurrentValueAmplitude())
        self.currentValueAmplitudeLabel.grid(row=0, column=0, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))

        self.sliderAmplitude = ttk.Scale(self, from_=0, to=255, orient=tk.HORIZONTAL, command=self.sliderChangedAmplitude,variable=self.maxAmplitudeCurrentValue)
        self.sliderAmplitude.set(0)
        self.sliderAmplitude.grid(row=1, column=0, columnspan=2, sticky='ew', padx=self.xPadding)

        self.sliderFreqLabel = ttk.Label(self, text="Period [s]")
        self.sliderFreqLabel.grid(row=2, column=1, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))

        self.freqCurrentValue = tk.DoubleVar()
        self.currentValueFreqLabel = ttk.Label(self, text=self.getCurrentValueFreq())
        self.currentValueFreqLabel.grid(row=2, column=0, columnspan=1, sticky='w', padx=self.xPadding, pady=(10,0))

        self.sliderFreq = ttk.Scale(self, from_=0.2, to=5, orient=tk.HORIZONTAL, command=self.sliderChangedFreq,variable=self.freqCurrentValue)
        self.sliderFreq.set(1)
        self.sliderFreq.grid(row=3, column=0, columnspan=2, sticky='ew', padx=self.xPadding)
    
        self.actuationTypeLabel = ttk.Label(self, text="Actuation Type")
        self.actuationTypeLabel.grid(row=4,sticky='w', padx=self.xPadding, pady=(10,0))

        self.actuationTypeMenu = ttk.OptionMenu(
            self,
            self.optionActVar,
            self.actuationTypes[0],
            *self.actuationTypes, command=self.actuationTypeChanged)
        self.actuationTypeMenu.grid(row=5,columnspan=2, sticky="ew", padx=self.xPadding)

        self.startButton = ttk.Button(self, text="Start Task", command=self.parent.startTask)
        self.startButton.grid(row=6, column=0, sticky='w', padx=self.xPadding, pady=(10,0))

        self.stopButton = ttk.Button(self, text="Stop Task", command=self.parent.stopTask)
        self.stopButton.grid(row=6, column=1, sticky='e', padx=self.xPadding, pady=(10,0))
        
    def getCurrentValueAmplitude(self):
        return '{: .0f}'.format(self.maxAmplitudeCurrentValue.get())

    def sliderChangedAmplitude(self, event):
        self.currentValueAmplitudeLabel.configure(text=self.getCurrentValueAmplitude())
        if(not self.parent.continueRunning):
            self.parent.createSignal()

    def getCurrentValueFreq(self):
        return '{: .1f}'.format(self.freqCurrentValue.get())

    def sliderChangedFreq(self,event):
        self.currentValueFreqLabel.configure(text=self.getCurrentValueFreq())
        self.parent.createSignal()

    def actuationTypeChanged(self,event):
        self.parent.createSignal()
        
class graphData(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.create_widgets()

    def create_widgets(self):
        self.graphTitle = ttk.Label(self, text="Voltage Input STATIC")
        self.fig = Figure(figsize=(7,5), dpi=100)
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_title("Voltage Input Preview")
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.graph.get_tk_widget().pack()

    


#Creates the tk class and primary application "actuationUI"
root = tk.Tk()
app = actuationUI(root)

#start the application
app.mainloop()