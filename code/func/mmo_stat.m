function Job = mmo_isc(Job)

Job = defaultjob(struct(TimeOfInterestSec=[-3, 3], WindowSec=6, HopProp=0.5), Job, mfilename);


end