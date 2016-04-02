# -*- coding: utf-8 -*-
import pylab as p
import numpy as np
import scipy.signal as ss
#wczytwanie pliku
surowy=np.fromfile('C:/Users/Pawel/Desktop/EKG/ekg_hr2.raw','float32')
lprob=len(surowy)
print lprob
surowy=np.reshape(surowy,(lprob/4,4))
print surowy
surowy=surowy.transpose()

F=512.

#definicja filtrow
def filtr_highpass(syg,Fs):
    [b,a]=ss.butter(5,10./(Fs/2.0),'highpass')
    return ss.filtfilt(b,a,syg)
    
def filtr_bandstop(syg,Fs):
    [b,a]=ss.butter(5,[48./(Fs/2.0),52./(Fs/2.0)],'bandstop')
    return ss.filtfilt(b,a,syg)

def filtr(syg,Fs):
    return filtr_bandstop(filtr_highpass(syg,Fs),Fs)

#montaz
lewa=surowy[:][0]
#zerowy wiersz to lewa ręka
#pierwszy wiersz to prawa ręka
prawa=surowy[:][1]
stopa=surowy[:][2]
gnd=surowy[:][3]



#montaz einthovena
#I
sygI=prawa-lewa

#II
sygII=stopa-prawa
#III
sygIII=stopa-lewa

#filtrowanie einthovena
einI=filtr(sygI,F)
einII=filtr(sygII,F)
einIII=filtr(sygIII,F)[0:18000]


#150 - 350

iloczyn_skalarny=np.zeros(len(einIII)-200)
for i in range(len(einIII)-200):
    iloczyn_skalarny[i]=np.inner(einIII[150:350],einIII[i:i+200])

#---Wykres iloczynu skalarnego
p.clf()
x=[]
y=[]
for i in range(2000):
    x.append(i/F)
    y.append(iloczyn_skalarny[i])
p.plot(x,y)

p.ylabel('iloczyn skalarny')
p.xlabel('Czas[s]')
#p.ylabel('I')
p.savefig('C:/Users/Pawel/Desktop/EKG/iloczyn_skalarny_hr2.png')
p.show()



"""
#---Wykres einIII
p.clf()
x=[]
y=[]
for i in range(len(einIII)):
    x.append(i/512.)
    y.append(einIII[i])
p.plot(x,y)

p.ylabel('EinthovenIII')
p.xlabel('Czas[s]')
#p.ylabel('I')
p.show()
"""


#ta funkcja zamienia sygnal na sygnal binarny z zalamkami 1 a reszta 0
def binarny(syg):
    	
    y=syg

    binar=np.zeros(len(y))
    
    #wyszukuje pikow
    zakres=1000
    for i in range(1,int(len(y)/zakres)):
	przedzial=y[(i-1)*zakres:i*zakres]
	prog=0.6*przedzial[np.argmax(przedzial)]
	print prog
	for j in range((i-1)*zakres,i*zakres):
		if y[j]>=prog:
			binar[j]=1
    #zamieniam piki na punkty
    binarny_dobry=np.zeros(len(binar)-1)
    l=-30
    for i in range(len(binar)-1):
        if binar[i+1]==1:
            if binar[i]==0:
               # print i
                if i-l>20:
                    binarny_dobry[i+1]=1
                    l=i
    return binarny_dobry  
    
    
def oblicz_tetno(poprzedni,nastepny):
    return 60*512./(float(nastepny-poprzedni))

#funkcja obliczajaca tetno          
def tetno(syg):
    syg_tetno=np.zeros(len(syg))
    poprzedni=0
    nastepny=0
    for i in range(len(syg)):
        if syg[i]==1:
            poprzedni=nastepny
            nastepny = i
            if poprzedni!=0:
                syg_tetno[i]=oblicz_tetno(poprzedni,nastepny)
    return syg_tetno
    
    
   
einIII_t=tetno(binarny(iloczyn_skalarny))

p.clf()
#wykres zaleznosci tetna od czasu
x=[]
y=[]
suma=0
ilosc=0
for i in range(len(einIII_t)):
    if einIII_t[i]!=0:
        print i
        x.append(i/F)
        y.append(einIII_t[i])
        suma+=einIII_t[i]
        ilosc+=1
        
        
pole=0
for i in range(len(x)-1):
    pole+=((y[i]+y[i+1])/2)*(x[i+1]-x[i])
    

#p.plot(binarny(einI))
p.plot(x,y)
p.xlabel('czas [s]')
p.ylabel('Tetno')
p.title('Zaleznosc tetna od czasu')
p.savefig('C:/Users/Pawel/Desktop/EKG/tetno_EinIII_hr2.png')
p.show()

print "srednie tetno wynosi : "+str(pole/(x[len(x)-1]-x[0]))
