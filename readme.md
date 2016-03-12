# animation.py

Animation and timer for pygame games
animation.py is public domain.

* [Tasks: Delayed calls](#task)
* [Animation: Change values over time](#animation)


# Task
## Execute functions at a later time, once or many times

This is a silly little class meant to make it easy to create
delayed or looping events without any complicated hooks into
pygame's clock or event loop.

Tasks do not have their own clock, and must get their time
from an update.  Tasks can be added to a normal sprite group
to get their time if you have several Tasks running at once.

When a task or animation finishes or is aborted, they will be
removed from the animation group, so there is no need to worry
about managing instance of the Tasks or Animations.

The only real requirement about the group, is that it must
not be drawn.

### Examples

Because the pygame clock returns milliseconds, the examples
below use milliseconds.  However, you are free to use what-
ever time unit you wish, as long as it is used consistently

The Task class is used to schedule the execution of functions
at some point the the future.  Below is a demonstration.
Eventually, the function "call_later" will be called once.

```python
import pygame

task_group = pygame.sprite.Group()

def call_later():
    pass

# call_later will now be called after 1 second
task = Task(call_later, 1000)
task_group.add(task)

clock = pygame.clock.Clock()
while game_is_running:
    dt = clock.tick()
    task_group.update(dt)
```


If you want to repeat the function, then pass another value.
Below, the "call_later" function will be called 24 times, with
1000 milliseconds between each call.

```python
task = Task(call_later, 1000, 24)
```


Set times to -1 to make the task repeat forever, or until aborted.

```python
task = Task(call_later, interval=2500, times=-1)
```


Tasks must be initialized with at least one callback, but more
can be added later on.

```python
task = Task(heres_my_number, 2500, -1)
task.schedule(call_me)     # schedule something else
task.schedule(maybe)       # schedule something else
```


The Task and Animation classes do not directly support passing
positional or keyword arguments to the scheduled callback
functions.  In order to do so, use the standard library function
"partial" found in functools.

```python
from functools import partial

task = Task(partial(call_later(1,2,3, key=value)), 1000)

# or schedule using a partial:
task.schedule(partial(call_later(1,2,3, key=value)), 1000)
```


There are other useful ways to schedule with a Task:

```python
# Task that does my_function 10x with 1 second interval
task = Task(my_function, 1000, 10)

# "quit" will be called after the 10th time (when task is totally finished)
task.schedule(quit, 'on finish')
```


Tasks support simple sequencing.  Use the chain method to
create a sequence of tasks.  Chained events will begin after
the task has finished.  Chaining can be useful if tasks are
aborted, or if you don't care to, or can't compute the time
it takes a complex sequence of actions takes.

When chaining tasks, do not add the chained tasks to a group.

```python
task = Task(call_later, 2500)        # after 2.5 seconds
task.chain(Task(something_else, 1))  # something_else is called 3.5 seconds later
```


# Animation
## Change numeric values over time

The animation class is modeled after Kivy's excellent
Animation module and is adapted for pygame.  It is similar,
but not a direct copy.

### What it does

Animation objects are used to modify the attributes of other
objects over time.  It can be used to smoothly move sprites
on the screen, fade surfaces, or any other purpose that involves
the smooth transition of one value to another.

Animations (and Tasks) are meant to follow the pygame "Sprite
and Group" model.  They do not implement their own clock, rather,
they rely on being updated, just like sprites.


### Examples

To animate a target sprite/object's position, simply specify
the target x/y values where you want the widget positioned at
the end of the animation.  Then add the animation to a group.

Animations will smoothly change values over time.  So, instead
of thinking "How many pixels do I add to move the rect?", you
can define where you want the rect to be, without thinking
about the math.


```python
import pygame

# this group will be only used to hold animations and tasks
animations = pygame.sprite.Group()

# create an animation to move a rect on the screen.
# the x and y values below correspond to the x and y of
# sprite.rect
ani = Animation(sprite.rect, x=100, y=100, duration=1000)

# animations do not have a clock, so they must be updated
# since they behave like pygame sprites, you can add them to
# a sprite group, and they will be updated from the group
animations.add(ani)

# game loop
while game_is_running:
    ...
    time_delta = clock.tick()
    animations.update(time_delta)
    ...
```


The shorthand method of starting animations is to pass the
targets as positional arguments in the constructor.
If you don't know the target when the animation is created,
you can use the `start` method to assign targets

```python
# make an animation, but don't assign a target
ani = Animation(x=100, y=0)

# assign the animation to change this rect
# (only call start once)
ani.start(sprite.rect)
```


If you would rather specify relative values, then pass the
relative keyword and the values will be adjusted for you.
Below, the rect will be moved 100 pixels to the right and
100 pixels down.

```python
ani = Animation(sprite.rect, x=100, y=100, duration=1000, relative=True)
```


Animations can also be configured for a delay.

```python
# start the movement after 300ms
ani = Animation(sprite.rect, x=100, y=100, duration=1000, delay=300)
```


Sometimes you need to stop an animation for a particular object,
but you don have a reference handy for it.  Use the included
remove_animations_of function to do just that

```python
from animation import Animation, remove_animations_of

# make an animation for this sprite
ani = Animation(sprite.rect, x=100, y=100, duration=1000)
animations.add(ani)


# oops, the sprite needs to be removed from the game;
# lets remove animations of the rect
remove_animations_of(sprite.rect, animations)
```


Animations can be aborted or finished early.  Finishing an animation
will cause the animation to end, but the target values will be applied.
Aborting an animation will not change the values.

```python
ani = Animation(sprite.rect, x=100, y=100, duration=1000)

ani.abort()   # animation stops; rect will be where it was when canceled
ani.finish()  # animation stops, but sprite will be moved to 100, 100
```

You can also specify a callback that will be executed when the
animation finishes:

```python
# "my_function" will be called after the animation finishes
ani.schedule(my_function, 'on finish')

# "on finish" can be omitted; the following line is equivalent to the above
ani.schedule(my_function)

# Other optional callback times are available
ani.schedule(func, 'on update')  # called after new values are applied each update
```


### Callable Attributes

Target attributes can also be callable.  If callable, they will be called
with the value of the animation each update.  For example, if you are
using an Animation on the "set_alpha" method of a pygame Surface, then
each update, the animation will call Surface.set_alpha(x), where x is
a value between the initial value and final value of the animation.

This presents a special problem, as it may be impossible to
determine the initial value of the animation.  In this case, the
following rules are used to determine the initial value of the animation:

* If the callable returns a value, the initial value will be set to that
* If there is no return value (or it is None), the initial will be zero

To further complicate matters the the initial value can be passed
in the Animation constructor.  If passed, the value returned by the
callable will not be considered.  The initial value can also be a
callable, and is subject to the following rules: 

* The value of the initial or return value of it are used
* The initial must be a number
* If the initial is None (or any other non-number), an exception is raised
* The initial value is only determined once

NOTE: Specifying an initial value will set the initial value
      for all target names in the constructor.  This
      limitation won't be resolved for a while.
            
### Example of using callable attributes

```python
import pygame

surf = pygame.image.load("some_sprite.png")

# this animation will change the alpha value of the surface
# from 0 (the default) to 255 over 1 second
ani = Animation(surf, set_alpha=255, duration=1000)

# you can also specify the initial value
# the following will fade from 255 to 0
ani = Animation(surf, set_alpha=0, initial=255, duration=1000)
```



### Rounding

In some cases, you may want you values to be rounded to the 
nearest integer.  For pygame rects, this is needed for smooth
movement, and the Animation class will use rounded values
automatically.  For other cases, pass "round_values=True"

### Potential pitfalls

Because Animations have a list of keyword arguments that configure
it, those words cannot be used on target objects.

For example, because "duration" is used to configure the Animation,
you cannot use an animation to change the "duration" attribute of
another object.  This is an issue that I will fix sometime.

For now, here is a list of reserved words can cannot be used:
* duration
* transition
* initial
* relative
* round_values
* delay


### More info

The docstrings have some more detailed info about each class.  Take
a look at the source for more info about what is possible.
