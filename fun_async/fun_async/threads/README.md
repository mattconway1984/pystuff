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
