animation.py
============

Animation helper for pygame games

animation.py is public domain.


Animation: Change numeric values over time
==========================================


To animate a target sprite/object's position, simply specify
the target x/y values where you want the widget positioned at
the end of the animation.  Then call start while passing the
target as the only parameter.

```python
ani = Animation(x=100, y=100, duration=1000)
ani.start(sprite)
```


The shorthand method of starting animations is to pass the
targets as positional arguments in the constructor.

```python
ani = Animation(sprite.rect, x=100, y=0)
```


If you would rather specify relative values, then pass the
relative keyword and the values will be adjusted for you:

```python
ani = Animation(x=100, y=100, duration=1000, relative=True)
ani.start(sprite)
```


You can also specify a callback that will be executed when the
animation finishes:
```python
ani.schedule(my_function, 'on finish')
```


Another optional callback is available that is called after
each update:
```python
ani.schedule(my_function, 'on update')
```


Animations must be added to a sprite group in order for them
to be updated.  If the sprite group that contains them is
drawn then an exception will be raised, so you should create
a sprite group only for containing Animations.

You can cancel the animation by calling Animation.abort().

When the Animation has finished, then it will remove itself
from the sprite group that contains it.

You can optionally delay the start of the animation using the
delay keyword.


Callable Attributes
===================

Target values can also be callable.  In this case, there is
no way to determine the initial value unless it is specified
in the constructor.  If no initial value is specified, it will
default to 0.

Like target arguments, the initial value can also refer to a
callable.

NOTE: Specifying an initial value will set the initial value
      for all target names in the constructor.  This
      limitation won't be resolved for a while.


Pygame Rects
============

The 'round_values' parameter will be set to True automatically
if pygame rects are used as an animation target.



Task: Execute functions at a later time, once or many times
===========================================================


This is a silly little class meant to make it easy to create
delayed or looping events without any complicated hooks into
pygame's clock or event loop.

Tasks are created and must be added to a normal pygame group
in order to function.  This group must be updated, but not
drawn.

Because the pygame clock returns milliseconds, the examples
below use milliseconds.  However, you are free to use what-
ever time unit you wish, as long as it is used consconsistently

```python
task_group = pygame.sprite.Group()

# like a delay
def call_later():
    pass
task = Task(call_later, 1000)
task_group.add(task)

# do something 24 times at 1 second intervals
task = Task(call_later, 1000, 24)

# do something every 2.5 seconds forever
task = Task(call_later, 2500, -1)

# pass arguments using functools.partial
from functools import partial
task = Task(partial(call_later(1,2,3, key=value)), 1000)

# a task must have at lease on callback, but others can be added
task = Task(call_later, 2500, -1)
task.schedule(some_thing_else)

# chain tasks: when one task finishes, start another one
task = Task(call_later, 2500)
task.chain(Task(something_else))

When chaining tasks, do not add the chained tasks to a group.
```
