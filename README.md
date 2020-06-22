# jabber_home_cluster
Jabber Home Cluster Reconcilation
Problem: Expressway registration failures for Jabber voice due to "Home Cluster" configuration problem.

Our company has 24 CUCM clusters with Jabber voice users on each of these clusters. 
When users connect via Expressway, the "Home Cluster" setting determines where the Jabber user tries to connect. 
Because of our AD structure, users can be in multiple CUCM clusters and the "Home Cluster" 
setting can get inadvertently set in the wrong CUCM. This can yield intermittent 
Expressway registrations and a very frustrated user with difficult troubleshooting. 
The "Home Cluster" default in CUCM was changed to disable, to mitigate some of these problems.

This program builds a list of all CSF devices and a list of all users. 
It then makes an assessment if "Home Cluster" is selected on the correct CUCM cluster and 
creates an exception list emailed to a group of administrators.

This program takes hours to run, so it is automatically run a 9 PM twice per week. 
It has reduced the support desk tickets, but more importantly the user frustration and 
what was perceived as the intermittent nature of Expressway registrations.
