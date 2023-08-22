from tkinter import *
 
def click_me():
    print(i.get())
 
root =Tk()
i=IntVar()
c = Checkbutton(root, text = "Python", variable=i)
c.pack()
 
b = Button(root,text="Click here",command=click_me)
b.pack()
 
root.geometry("400x400+120+120")
root.mainloop()