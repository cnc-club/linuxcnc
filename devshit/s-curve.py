from math import *
import cairoplot
class TC(): 
	current_accel=0.
	currentvel=0.
	jerk=0.
	maxaccel=0.
	maxvel=0.
	target=0.
	progress=0.
	cycle_time = 0.001	
	reqvel = 100.
	feed_override =1.
	current_jerk = 0.

pr = False
da = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,]
state = -1	


def get_deccel_dist(tc,v,a,j) :
	d2=0.
	d4=0.
	d5=0.
	d6=0.	
	jerk = 0.

	if v<0 : 
		if pr : print "v<0",v
		return 0.
	t = tc.cycle_time 
	d = v*t + a*t*t/2. + j*t*t*t/6.
	vel = v + a*t+j*t*t/2.
	accel = a + j*t
	jerk_time = tc.maxaccel/tc.jerk
	jerk_vel = 0.5 * tc.maxaccel * jerk_time

	if accel > 0. : # # we are accelerating now  
		t = ceil(accel/tc.jerk/tc.cycle_time)*tc.cycle_time # # max = maxaccel/jerk in any case
		#t = accel/tc.jerk # # max = maxaccel/jerk in any case
		#jerk = accel/t
		d2 = vel * t + 0.5 * accel * t * t - 1.0/6.0 * tc.jerk * t * t * t
		#if pr : print vel,t,accel,tc.jerk,d2	
		vel += accel * t - 0.5 * tc.jerk * t * t  # get velocity add after stopping acceleration
		accel = 0. # after finishing acceleration accel will be 0
	t = -accel/tc.jerk	# get the time, we have been deccelerated a<=0
	
	#if pr :print d4,t,vel
	vel += 0.5*tc.jerk*t*t
	
	d4 -= vel*t - 1.0/6.0*tc.jerk*t*t*t # asume we only have started decceleration. 
	if pr :print 
	#if pr :print d4,t,vel
	#accel = 0.
	# now t4 and t6 are equal 
	# 
	
	if vel > 2.0*jerk_vel :
		# there's t5 - deccel on maxaccel
		t = (vel - 2.0*jerk_vel) / tc.maxaccel
		t = ceil(t/tc.cycle_time)*tc.cycle_time
	#	if pr : print "t ", t
		d5 = (vel-jerk_vel)*t - 0.5*tc.maxaccel*t*t
		t = jerk_time
		#print "D%!!!!!!!"		
	else :
		t = sqrt(vel/tc.jerk) # only t4 and t6 
	#if pr :print d4, vel, t
	t = ceil(t/tc.cycle_time)*tc.cycle_time
	#if (-t+accel/tc.jerk)>tc.cycle_time :
	d4 += vel*t - 1.0/6.0*tc.jerk*t*t*t
	#else:
	#	d4 = 0.
	d6 = 1.0/6.0*tc.jerk*t*t*t
	#if pr :print d4,t 
	#if vel - 4*j*t*t/2. < 0 : return 0
	
	if d4<=0 :
		if pr : print "d4<0",d4 
		return 0.
	d = d2+d4+d5+d6
	if pr :print ["%8.5f"%s for s in [d2,d4,d5,d6]],[v,a],[tc.target-tc.progress]
	return d

	
	
def tcRunCycle(tc):
	t=tc.cycle_time	
	p = tc.target  - tc.progress
	
	d = get_deccel_dist(tc,tc.currentvel,tc.current_accel, tc.jerk)	
	tc.d = d	
	if pr : print d," - p",p, "*** %s ***"%(p-d)
	if pr : print tc.currentvel, tc.current_accel
	if d<p : jerk =  tc.jerk #D0
	else : jerk =  -tc.jerk #D2
	
	accel = tc.current_accel + jerk*t
	if (accel>0 and accel>tc.maxaccel) : 
		accel = tc.maxaccel
		jerk = (accel-tc.current_accel)/t

	if (accel<0 and accel<-tc.maxaccel) : 
		accel = -tc.maxaccel
		jerk = (accel-tc.current_accel)/t
		
	
	vel = tc.currentvel + tc.current_accel*t + 0.5*jerk*t*t 		
	reqvel = tc.reqvel * tc.feed_override
	if reqvel > tc.maxvel : reqvel = tc.maxvel
	if vel > reqvel :  
		vel = reqvel	 # clamp vel 
		jerk = 2.*(vel-tc.currentvel-tc.current_accel*t)/t/t# new jerk
			
		
	# check velocity limit
	if accel>0 and jerk>=0 : # need only if we are accelerating
		d1 = (accel*accel) - 2.*(reqvel-vel)*tc.jerk # v = v0 + a*t + j*t/2   d = a*a - 4*j/2*
		if d1>0 :
			t1 = (accel + sqrt(d1))/tc.jerk
			if t1<sqrt(2.*(tc.reqvel-vel)/tc.jerk) : # weneed to start to deccel
				jerk = -tc.jerk

	
	tc.progress += tc.currentvel*t + 0.5*tc.current_accel*t*t + 1.0/6.0*jerk*t*t*t
	vel = tc.currentvel + tc.current_accel*t + 0.5*jerk*t*t 	
	accel = tc.current_accel + jerk*t
	tc.currentvel = vel
	tc.current_accel = accel
	tc.current_jerk = jerk
	
	
	
data =[]
# target, progress, maxvel,maxa,jerk, cura, curvel
from random import *
test = [[200.,0.,200.,1000.,1200.521,0.,0.] ] #+ [[random()*5 +2.,0.,random()*4+.2,random()+1.,random()+.01,0.,0.]  for i in range(4)]
n=0
for test1 in test:
	tc = TC()
	tc.target, tc.progress, tc.maxvel, tc.maxaccel, tc.jerk,tc.current_accel,tc.currentvel=tuple(test1)
	tc.d6_=0	

	data.append([[],[],[],[],[],[],[],])	
	for i in range(80000) :
		tcRunCycle(tc)
		if tc.target<=tc.progress or tc.currentvel<0.: break
		if i%100 :
			data[-1][6] += [min(5,(tc.target-tc.progress-tc.d)*10.) ]
			data[-1][1] += [tc.progress]
			data[-1][2] += [tc.currentvel]
			#print tc.currentvel
			data[-1][3] += [tc.current_accel]
			data[-1][4] += [tc.d]
			data[-1][5] += [0]#,tc.maxvel]
			data[-1][0] += [tc.current_jerk]#[(tc.d-tc.target)*10 if tc.d-tc.target>0 else 0]
			#if pr : print tc.target-tc.progress-tc.d
			pr = i%1000==0 
	
			#if pr : print "\n",i,"\n%4.5f %4.5f v%4.5f a%4.5f j%4.5f %4.5f %4.5f "% (tc.target, tc.progress, tc.currentvel, tc.current_accel, tc.current_jerk, tc.maxvel, tc.maxaccel)
			if pr : print "\n", i		
	print tc.d," - p", 
	print tc.target - tc.progress,  tc.target <=tc.progress
	print tc.currentvel, tc.current_accel
		
	n+=1
	cairoplot.dot_line_plot ("test%d.png"%n,
						 data[-1],
						 800,
						 600,
 			background = (.95,.95,.95),
					border = 0,
					axis = False,
					grid = True,
					dots = False,
					series_colors = [(.8,0,0),(0,0.8,0),(0,0,0.8),(.4,0.4,1),(.4,0,0.4),(0,0.4,0.4),(.4,.4,0.4),]
)

