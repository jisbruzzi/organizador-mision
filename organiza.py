import csv

#AGARRAR LOS DATOS DEL ARCHIVO DE MISIONEROS
misioneros={};
with open("misioneros.csv") as csvfile:
	reader = csv.reader(csvfile)
	
	
	
	primero = True;
	for row in reader:
		if primero:
			primero=False
			continue
		
		datosMisionero={}
		datosMisionero["nombre"]=row[0]
		datosMisionero["fraile"]=row[1]
		datosMisionero["viejo"]=row[2]
		datosMisionero["asado"]=row[3]
		datosMisionero["enRetiro"]=row[4]
		
		misioneros[row[0]]=datosMisionero
		
#CARGAR DATOS DEL ARCHIVO DE BARRIOS
barrios=[]
with open("barrios.csv") as csvfile:
	reader = csv.reader(csvfile)
	
	primero = True;
	for row in reader:
		barrios.append(row)
		for m in row:
			if not (m in misioneros.keys()):
				print(m+" no esta en la lista de misioneros !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

print(barrios)

#PLANTEAR EL PROBLEMA

from pulp import * 
dias = range(4,15)#del 4 al 14/1
horarios=["maniana","tarde"]
nMisioneros=misioneros.keys()

servicioMDH=LpVariable.dicts("servicioMDH",[(m,d,h) for m in nMisioneros for d in dias for h in horarios], 0, 1, cat='Integer')

prob=LpProblem("Servicios", pulp.LpMinimize)

def servicios(m=-1,d=-1,h=-1):
	_m = [m] if m!=-1 else nMisioneros
	_d = [d] if d!=-1 else dias
	_h = [h] if h!=-1 else horarios
	return sum(servicioMDH[(mm,dd,hh)] for dd in _d for mm in _m for hh in _h)

#objetivo: minimizar los servicios de los nuevos
def esNuevo(nombre):
	return int(misioneros[nombre]["viejo"])==0

prob+=sum(servicioMDH[(mm,dd,hh)] for dd in dias for hh in horarios for mm in filter(esNuevo,nMisioneros));
#prob+=0


#menos de 3 servicios por persona
for m in nMisioneros:
	prob+=servicios(m=m)<=3

#mas de 2 servicios por persona
for m in nMisioneros:
	prob+=servicios(m=m)>=2
	
#que haya como mucho un servicio mas en un horario que en otro (manianas-1<=tardes<=manianas+1) para todo misionero
for m in nMisioneros:
	prob+= servicios(m=m,h="tarde") -servicios(m=m,h="maniana") <=1
	prob+= servicios(m=m,h="maniana")-servicios(m=m,h="tarde") <= 1
	
#el 8 cumple tomie
prob += servicios(m="tomie",d=8)==0

#el 13 cumple rochi
prob += servicios(m="rochi",d=8)==0

#el 9 michel sale a comprar a la tarde, debe estar de servicio
prob += servicios(m="michel",d=9,h="tarde")==1

#el 6 tashi y carlos salen a comprar a la tarde, deben estar de servicio
prob += servicios(m="tashi",d=6,h="tarde")==1
prob += servicios(m="carlos",d=6,h="tarde")==1

#4 personas por servicio
for d in dias:
	for h in horarios:
		prob+= servicios(d=d,h=h)==4

#jueves 4 y viernes 5 solo los que trabajan en el retiro
for d in [4,5]:
	for m in nMisioneros:
		if int(misioneros[m]["enRetiro"])==0:
			prob += servicios(d=d,m=m)==0
			
#entre el 4 y el 5 se tiene como mucho un servicio
for m in nMisioneros:
	prob+= servicios(m=m,d=4)+servicios(m=m,d=5)<=1

#maximo un fraile por servicio
def esFraile(nombre):
	return int(misioneros[nombre]["fraile"])==1
for d in dias:
	for h in horarios:
		prob += sum(servicioMDH[(mm,d,h)] for mm in filter(esFraile,nMisioneros))<=1
		
#Fr Carlos no puede cuando hay procesion, misa o bautismos
prob += servicios(m="carlos",d=10,h="tarde")==0 #procesion
prob += servicios(m="carlos",d=11,h="tarde")==0 #misa cementerio
prob += servicios(m="carlos",d=13,h="tarde")==0 #bautismos

#tatu, chiqui y tincho no pueden antes del sabado 7 inclusive
for m in ["tatu","chiqui","tincho"]:
	for d in filter(lambda x: x<=7,dias):
		prob+= servicios(m=m,d=d)==0
		
#en cada servicio puede haber como mucho un misionero de cada barrios
for barrio in barrios:
	for h in horarios:
		for d in dias:
			prob += sum(servicioMDH[(mm,d,h)] for mm in barrio)<=1
		
#no puede ser que una persona este de servicio a la maniana y a la tarde el mismo dia
for m in nMisioneros:
	for d in dias:
		prob += servicios(m=m,d=d,h="maniana") + servicios(m=m,d=d,h="tarde")<=1

#no puede ser que una persona este de servicio a la tarde un dia y a la maniana el siguiente
for m in nMisioneros:
	for d in dias:
		if (d+1) in dias:
			prob += servicios(m=m,d=(d+1),h="maniana") + servicios(m=m,d=d,h="tarde")<=1
		
#resolver el problema y mostrarlo
prob.writeLP("modeloMisioneros.lp")
prob.solve()


for d in dias:
	for h in horarios:

		print("dia "+str(d)+" horario "+str(h)+":")
		
		for m in nMisioneros:
			if servicioMDH[(m,d,h)].value()==1.0:
				print(m)
	print("")
				
for m in nMisioneros:
	servicios=0
	for d in dias:
		for h in horarios:
			servicios+=servicioMDH[(m,d,h)].value()
	print(m+" tiene "+str(servicios)+" servicios")

print("Status:", LpStatus[prob.status])