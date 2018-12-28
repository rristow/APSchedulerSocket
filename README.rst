The purpose of the application is to solve the problem of having a unique 'APScheduler' object for a multithreaded application. The project aims to easily implement a client-server architecture to control the scheduled processes. Another advantage is that you can use the scheduler in distributed processes or servers.

INSTALL
=======

::

    $ pip install APSchedulerSocket

USAGE
=====

::

    from apschedulersocket import schedulers
    from datetime import datetime

    def my_process():
        print("Executing my process: Hello world!")

    # Show the protocol messages
    schedulers.DEBUG = True

    # New SchedulerServer
    scheduler = schedulers.SchedulerServer(daemon=False)

    # Check if the server was not already started by another thread/process
    if not scheduler.client.is_server_running():
        scheduler.add_job(func=my_process,
                          id="my_process",
                          trigger='interval',
                          next_run_time=datetime.now(),
                          minutes=1)
        # start the apscheduler and the server
        print("Server started!")
        scheduler.start()

    print("Server state (1=running):",
          scheduler.client.call(["BackgroundScheduler","state"]))

    print("The next run time of my_process:",
          scheduler.client.call(["my_process","next_run_time"]))

    print("Pause the job:",
          scheduler.client.call(["my_process","pause"]))

    print("Next run time of paused my_process (None=paused):",
          scheduler.client.call(["my_process","next_run_time"]))

    print("Resume the job:",
          scheduler.client.call(["my_process","resume"]))

    print("Wrong message to server:",
          scheduler.client.call(["Can you also cook?",]))

    print("Shutdown!",
          scheduler.client.call(["shutdown",]))


DEVELOP
=======

::

    $ git clone https://github.com/rristow/APSchedulerSocket APSchedulerSocket
    $ cd APSchedulerSocket
    $ make

RUNNING TESTS
=============

::

    $ make test
    # TODO!