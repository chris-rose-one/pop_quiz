# Pop Quiz

This is a polling app with a dynamically created and updated bar graph as representation and a status panel to guide you every step of the way. It leverages the batteries included in the Django web framework to build a database backend and provide a CRUD administration system.

The real work horse of this application is django channels, in particular the web socket capabilities that they bring.
After the http page request and response is complete, messages between the server and client of poll updates,
vote choices or changes of mind are sent via websockets as an event requires them to be.<br/>
Essentially providing a live multi-user poll.

the bar graph is rendered using a javascript library d3.js (data driven documentation)

the poll has two different modes<br/>
<ol>
<li>free for all, unlimited votes &#42;<br/></li>
<li>one vote only &#42;<br/></li>
&#42; until a choice caps or voting closes.
</ol>

polls are created using the Django admin interface, here you may set the following parameters:
- question text
- starting time
- running time (voting period)
- remain active (for end result viewing)
- one vote only mode checkbox (enough said)
	- although, it does incorporate an undo button for the chance of mind changers.
- vote limit
	- this applies to the max votes any one choice may receive. not the overall poll
- and then there are the choices of answers
	- 4 choices fit my Samsung S5 nicely in free for all mode&#42;&#42;
	- 3 choices fit with the undo button, when in one vote only mode &#42;&#42;<br/>
    &#42;&#42; similar results when scaled up to a PC screen.

It is possible to queue up a number of polls ahead of time. a pre save signal wont allow poll times to overlap

Repository settings are configured ready to be deployed to Heroku and uses two main processes
- Daphne http/websocket server
- Django worker

And requires the support of
- Redis
- Postgresql

As time elapses, polls go through a series of changes; polls close, they end and new ones begin. 
these changes rely on time attributes within the model and an independent process to assess if one has come to pass before messaging these changes in state to clients.
upgrade Heroku and un-comment the fluidpoll worker in Procfile for autonomous real-time polling.