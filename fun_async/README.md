Overview
========

The problem that asynchrony seeks to resolve is blocking I/O.

By default, when your program accesses data from an I/O source, it waits for
that operation to complete before continuing to execute the program. The program
is blocked from continuing its flow of execution while a physical device is
accessed, and data is transferred. Network operations are another common source
of blocking.

In many cases, the delay caused by blocking is negligible. However, blocking I/O
scales very poorly. If you need to wait for 1010 file reads or network
transactions, performance will suffer.

Strategies for minimizing the delays of blocking I/O fall into three major
categories:

    1. multiprocessing
    2. threading
    3. asynchrony

Multiprocessing
===============
Instructions are executed in an overlapping time frame on multiple physical
processors or cores. Each process spawned by the kernel incurs an overhead cost,
including an independently-allocated chunk of memory (heap). Python implements
parallelism with the multiprocessing module.

Threading
=========
Threads are independently scheduled, and their execution may occur within an
overlapping time period. Unlike multiprocessing, however, threads exist entirely
in a single kernel process, and share a single allocated heap.

Python threads are concurrent. Multiple sequences of machine code are executed
in overlapping time frames but are not parallel. Execution does not occur
simultaneously on multipleOther High-level APIs

The primary downsides to Python threading are memory safety and race conditions.
All child threads of a parent process operate in the same shared memory space.
Without additional protections, one thread may overwrite a shared value in
memory without other threads being aware of it. Such data corruption would be
disastrous.

To enforce thread safety, CPython implementations use a global interpreter lock
(GIL). The GIL is a mutex mechanism that prevents multiple threads from
executing simultaneously on Python objects. Effectively, this means that only
one thread runs at any given time.

Asynchrony
==========
Asynchrony is an alternative to threading for writing concurrent applications.
Asynchronous events occur on independent schedules, "out of sync" with one
another, entirely within a single thread.

Unlike threading, in asynchronous programs the programmer controls when and how
voluntary preemption occurs, making it easier to isolate and avoid race
conditions.

Python asyncio API
==================

High-Level vs Low-Level asyncio API
-----------------------------------
Asyncio components are divided into high-level APIs (for writing programs), and
low-level APIs (for writing libraries or frameworks based on asyncio). Every
asyncio program can be written using only the high level APIs. If you're not
writing a framework or library, you never need to touch the low-level stuff.

Coroutines
----------
In general, a coroutine (short for cooperative subroutine) is a function
designed for voluntary preemptive multitasking: it proactively yields to other
routines and processes, rather than being forcefully preempted by the kernel.
The term "coroutine" was coined in 1958 by Melvin Conway (of "Conway's Law"
fame), to describe code that actively facilitates the needs of other parts of a
system. In asyncio, this voluntary preemption is called awaiting.

Awaitables, Async, and Await
----------------------------
Any object which can be awaited (voluntarily preempted by a coroutine) is called
an awaitable.The await keyword suspends the execution of the current coroutine,
and calls the specified awaitable.

In Python 3.7, the three awaitable objects are:

    1. coroutine

       An asyncio coroutine is any Python function whose definition is
       prefixed with the async keyword.

    2. task 

       An asyncio task is an object that wraps a coroutine, providing
       methods to control its execution, and query its status. A task may be
       created with asyncio.create_task(), or asyncio.gather(). If you await a i
       task, execution of the current coroutine is blocked until that task is
       complete.
       Tasks have several useful methods for managing the wrapped coroutine.
       Notably, you can request that a task be canceled by calling the task's
       .cancel() method. The task will be scheduled for cancellation on the
       next cycle of the event loop. Cancellation is not guaranteed: the task
       may complete before that cycle, in which case the cancellation does
       not occur.

    3. future

       An asyncio future is a low-level object that acts as a placeholder
       for data that hasn't yet been calculated or fetched. It can provide an
       empty structure to be filled with data later, and a callback mechanism
       that is triggered when the data is ready.

Event Loops
-----------
In asyncio, an event loop controls the scheduling and communication of awaitable
objects. An event loop is required to use awaitables. Every asyncio program has
at least one event loop. It's possible to have multiple event loops, but
multiple event loops are strongly discouraged in Python 3.7. A reference to the
currently-running loop object is obtained by calling asyncio.get_running_loop().

    1. Sleeping

       The asyncio.sleep(delay) coroutine blocks for delay seconds.  It's useful 
       for simulating blocking I/O.

    2. Initiating the Main Event Loop

       The canonical entrance point to an asyncio
       program is asyncio.run(main()), where main() is a top-level coroutine.
       Calling asyncio.run() implicitly creates and runs an event loop. The
       loop object has many useful methods, including loop.time(), which
       returns a float representing the current time, as measured by the loop's
       internal clock.
       Note: The asyncio.run() function cannot be called from within an
       existing event loop. Therefore, it is possible that you see errors if
       you're running the program within a supervising environment, such as
       Anaconda or Jupyter, which is running an event loop of its own.

Gathering Awaitables
--------------------
Awaitables can be gathered as a group, by providing them as a list argument to
the built-in coroutine asyncio.gather(awaitables). The asyncio.gather() returns
an awaitable representing the gathered awaitables, and therefore must be
prefixed with await. If any element of awaitables is a coroutine, it is
immediately scheduled as a task.

Gathering is a convenient way to schedule multiple coroutines to run
concurrently as tasks. It also associates the gathered tasks in some useful
ways:
    1. When all gathered tasks are complete, their aggregate return values are
       returned as a list, ordered in accordance with the awaitables list
       order.
    2. Any gathered task may be canceled, without canceling the other tasks.
    3. The gather itself can be cancelled, cancelling all tasks.
