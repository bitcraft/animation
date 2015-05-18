import sys

import pygame

from .transitions import AnimationTransition


__all__ = ('Task', 'Animation', 'remove_animations_of')

ANIMATION_NOT_STARTED = 0
ANIMATION_RUNNING = 1
ANIMATION_FINISHED = 2

PY2 = sys.version_info[0] == 2
string_types = None
text_type = None
if PY2:
    string_types = basestring
    text_type = unicode
else:
    string_types = text_type = str


def is_number(value):
    """Test if an object is a number.
    :param value: some object
    :return: True
    :raises: ValueError
    """
    try:
        float(value)
    except (ValueError, TypeError):
        raise ValueError

    return True


def remove_animations_of(group, target):
    """Find animations that target objects and remove those animations

    :param group: pygame.sprite.Group
    :param target: any
    :return: None
    """
    animations = [ani for ani in group.sprites() if isinstance(ani, Animation)]
    to_remove = [ani for ani in animations
                 if target in [i[0] for i in ani.targets]]
    group.remove(*to_remove)


class Task(pygame.sprite.Sprite):
    """Execute functions at a later time and optionally loop it

    This is a silly little class meant to make it easy to create
    delayed or looping events without any complicated hooks into
    pygame's clock or event loop.

    Tasks are created and must be added to a normal pygame group
    in order to function.  This group must be updated, but not
    drawn.

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

        # pass arguments
        task = Task(call_later, 1000, args=(1,2,3), kwargs={key: value})

        # chain tasks
        task = Task(call_later, 2500)
        task.chain(Task(something_else))

        When chaining tasks, do not add the chained tasks to a group.
    """

    def __init__(self, callback, interval=0, loops=1, args=None, kwargs=None):
        if not callable(callback):
            raise ValueError

        if loops < 1:
            raise ValueError

        super(Task, self).__init__()
        self.interval = interval
        self.loops = loops
        self.callback = callback
        self._timer = 0
        self._args = args if args else list()
        self._kwargs = kwargs if kwargs else dict()
        self._loops = loops
        self._chain = list()
        self._state = ANIMATION_RUNNING

    def chain(self, *others):
        """Schedule Task(s) to execute when this one is finished

        If you attempt to chain a task that will never end (loops=-1),
        then ValueError will be raised.

        :param others: Task instances
        :return: None
        """
        if self._loops <= -1:
            raise ValueError
        for task in others:
            if not isinstance(task, Task):
                raise TypeError
            self._chain.append(task)
        return others

    def update(self, dt):
        """Update the Task

        The unit of time passed must match the one used in the
        constructor.

        Task will not 'make up for lost time'.  If an interval
        was skipped because of a lagging clock, then callbacks
        will not be made to account for the missed ones.

        :param dt: Time passed since last update.
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        self._timer += dt
        if self._timer >= self.interval:
            self._timer -= self.interval
            self.callback(*self._args, **self._kwargs)
            if not self._loops == -1:
                self._loops -= 1
                if self._loops <= 0:
                    self._execute_chain()
                    self.abort()

    def abort(self):
        """Force task to finish, without executing callbacks
        """
        self._state = ANIMATION_FINISHED
        self._chain = None
        self.kill()

    def _execute_chain(self):
        groups = self.groups()
        for task in self._chain:
            task.add(*groups)


class Animation(pygame.sprite.Sprite):
    """Change numeric values over time

    To animate a target sprite/object's position, simply specify
    the target x/y values where you want the widget positioned at
    the end of the animation.  Then call start while passing the
    target as the only parameter.
        ani = Animation(x=100, y=100, duration=1000)
        ani.start(sprite)

    If you would rather specify relative values, then pass the
    relative keyword and the values will be adjusted for you:
        ani = Animation(x=100, y=100, duration=1000)
        ani.start(sprite, relative=True)

    You can also specify a callback that will be executed when the
    animation finishes:
        ani.callback = my_function

    Another optional callback is available that is called after
    each update:
        ani.update_callback = post_update_function

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

    If you are using pygame rects are a target, you should pass
    'round_values=True' to the constructor to avoid jitter caused
    by integer truncation.
    """
    default_duration = 1000.
    default_transition = 'linear'

    def __init__(self, **kwargs):
        super(Animation, self).__init__()
        self.targets = list()
        self.delay = kwargs.get('delay', 0)
        self._state = ANIMATION_NOT_STARTED
        self._round_values = kwargs.get('round_values', False)
        self._duration = float(kwargs.get('duration', self.default_duration))
        self._transition = kwargs.get('transition', self.default_transition)
        self._initial = kwargs.get('initial', None)
        if isinstance(self._transition, string_types):
            self._transition = getattr(AnimationTransition, self._transition)
        self._elapsed = 0.
        for key in ('duration', 'transition', 'round_values', 'delay',
                    'initial'):
            kwargs.pop(key, None)
        if not kwargs:
            raise ValueError
        self.props = kwargs

    def _get_value(self, target, name):
        """Get value of name, even if it is callable

        :param target: object than contains attribute
        :param name: name of attribute to get value from
        :return: Any
        """
        if self._initial is None:
            value = getattr(target, name)
        else:
            value = self._initial

        if callable(value):
            value = value()

        is_number(value)
        return value

    def _set_value(self, target, name, value):
        """Set a value on some other object

        If the name references a callable type, then
        the object of that name will be called with 'value'
        as the first and only argument.

        Because callables are 'write only', there is no way
        to determine the initial value.  you can supply
        an initial value in the constructor as a value or
        reference to a callable object.

        :param target: object to be modified
        :param name: name of attribute to be modified
        :param value: value
        :return: None
        """
        if self._round_values:
            value = int(round(value, 0))

        attr = getattr(target, name)
        if callable(attr):
            attr(value)
        else:
            setattr(target, name, value)

    def update(self, dt):
        """Update the animation

        The unit of time passed must match the one used in the
        constructor.

        Make sure that you start the animation, otherwise your
        animation will not be changed during update().

        Will raise RuntimeError if animation is updated after
        it has finished.

        :param dt: Time passed since last update.
        :raises: RuntimeError
        """
        if self._state is ANIMATION_FINISHED:
            raise RuntimeError

        if self._state is not ANIMATION_RUNNING:
            return

        self._elapsed += dt
        if self.delay > 0:
            if self._elapsed > self.delay:
                self._elapsed -= self.delay
                self.delay = 0
            return

        p = min(1., self._elapsed / self._duration)
        t = self._transition(p)
        for target, props in self.targets:
            for name, values in props.items():
                a, b = values
                value = (a * (1. - t)) + (b * t)
                self._set_value(target, name, value)

        if hasattr(self, 'update_callback'):
            self.update_callback()

        if p >= 1:
            self.finish()

    def finish(self):
        """Force animation to finish, apply transforms, and execute callbacks

        Update callback will be called because the value is changed
        Final callback ('callback') will be called
        Final values will be applied
        Animation will be removed from group

        Will raise RuntimeError if animation has not been started

        :return: None
        :raises: RuntimeError
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        if self.targets is not None:
            for target, props in self.targets:
                for name, values in props.items():
                    a, b = values
                    self._set_value(target, name, b)

        if hasattr(self, 'update_callback'):
            self.update_callback()

        self.abort()

    def abort(self):
        """Force animation to finish, without any cleanup

        Update callback will not be executed
        Final callback will be executed
        Values will not change
        Animation will be removed from group

        Will raise RuntimeError if animation has not been started

        :return: None
        :raises: RuntimeError
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        self._state = ANIMATION_FINISHED
        self.targets = None
        self.kill()
        if hasattr(self, 'callback'):
            self.callback()

    def start(self, target, **kwargs):
        """Start the animation on a target sprite/object

        Targets must have the attributes that were set when
        this animation was created.

        :param target: Any valid python object
        :raises: RuntimeError
        """
        # TODO: multiple targets
        # TODO: weakref the targets
        if self._state is not ANIMATION_NOT_STARTED:
            raise RuntimeError

        self._state = ANIMATION_RUNNING
        self.targets = [(target, dict())]
        for target, props in self.targets:
            relative = kwargs.get('relative', False)
            for name, value in self.props.items():
                initial = self._get_value(target, name)
                is_number(initial)
                is_number(value)
                if relative:
                    value += initial
                props[name] = initial, value
