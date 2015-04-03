animation.py
============

Animation helper for pygame games

this file is public domain


Change numeric values over time
===============================


To animate a target sprite/object's position, simply specify
the target x/y values where you want the widget positioned at
the end of the animation.  Then call start while passing the
target as the only parameter.

    ani = Animation(x=100, y=100, duration=1000)
    ani.start(sprite)

Change the animation tweening with the 'transition' keyword.
See the animation source for all the available tweening
functions. 

    ani = Animation(x=100, y=100, transition='in_quint')

Animations must be added to a sprite group in order for them
to be updated.  If the sprite group that contains them is
drawn, then an exception will be raised, so you should create
a sprite group only for containing Animations.

    ani = Animation(x=100, y=100, duration=1000)
    ani.start(sprite)
    group = pygame.sprite.Group()
    group.add(ani)
    group.update(time_passed_since_last_update)

When the Animation has finished, then it will remove itself
from the sprite group that contains it.

You can cancel the animation by calling Animation.kill().

    ani.kill()

You can optionally delay the start of the animation using the
delay keyword.

    # delay for 1000 ms
    ani = Animation(x=100, delay=1000)
    
    
Pygame Rects
============

If you are using pygame rects are a target, you should pass
'round_values=True' to the constructor to avoid jitter caused
by integer truncation.


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
