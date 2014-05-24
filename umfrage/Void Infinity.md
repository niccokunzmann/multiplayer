Q: What plans did you have to restructure your code? (I can look at the code myself but what were your ideas?)  
If I were to work on Void Infinity I would rewrite the entire game engine. Currently the way I write games makes it so that all I have to do is send "event" data that is constructed for things like ships and planets.

Q: What state needed to be shared between different game instances? Which state is only for single players?  
Before I would only send the user keyboard/mouse inputs between game instances, and attempt to simulate both games in sync. That method doesn't actually work, so my new system sends "event" data that tells the clients all of the important information about an object. Single player simply doesn't send data.

Q: Is that state lists, objects, classes, global? (Also hints at the code
would be good.)  
The way I used to program everything was global. I started to realize issues with doing it that way so now I have very few globals. Using my current method the event data would be stored in the associated objects class.

Q: Would you favor sending commands over synchronization of objects?  
Neither. Sending commands doesn't work: there needs to be some level of synchronization. If you synchronize objects the typical way you end up sending a lot of unnecessary information. My method only sends information when things change. Here's an example: Say a projectile collides with a ship and then a complicated damage model is ran which tells you that x rooms are destroyed, x weapons are destroyed, x damage is dealt to hp and whatever else. I wouldn't synchronize the entire ship that was damaged, I would send a damage event that tells other players the damage that was done. The damage event would also have a time associated with it so that if clients receive it late they can recalculate things if need be. An example of this is if a ship is destroyed but your calculations are off and it isn't in your game AND you haven't received the damage event yet and it shoots a projectile after it was destroyed. The recalculation would remove the projectile.

Q: If the line

    from multiplayer import *

would fulfill all your wishes. What would your code look like for your
game/a simple game/a chat client.  

	c_sock = Client()
	c_sock.connect((address,port),username,password) # This should open a threaded connection so that you don't have to wait to send/receive data.
	c_sock.send_data(data.encode())
	while running:
	    process_inputs()
	    for i in c_sock.recv_data():
	        do_things_with_data(i)

Q: My idea is currently to create synchronized datastructures such as lists, dicts, objects. What do you think about that?  
Keeping data structures constantly synchronized seems a bit tedious. There are a thousand ways to implement online games, choose whichever you find to be the easiest and most successful!