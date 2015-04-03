from math import sqrt, cos, sin, pi

__all__ = ('Animation', 'Animated', 'AnimationTransition')
__version__ = 0.1


ANIMATION_NOT_STARTED = 0
ANIMATION_RUNNING = 1
ANIMATION_FINISHED = 2


def is_number(value):
    try:
        float(value)
    except (ValueError, TypeError):
        raise ValueError

    return True


class Animated:
    """Use as a base class for a convenient way to animate things"""
    def animate(self, **kwargs):
        ani = Animation(**kwargs)
        ani.start(self)
        return ani


class Animation(object):
    """Change numeric values over time

    To animate a target sprite/object's position, simply specify
    the target x/y values where you want the widget positioned at
    the end of the animation.  Then call start while passing the
    target as the only parameter.
        ani = Animation(x=100, y=100, duration=1000)
        ani.start(sprite)

    If you would rather specify relative values, then pass the
    relative keyword, and the values will be adjusted for you:
        ani = Animation(x=100, y=100, duration=1000, relative=True)

    You can also specify a callback that will be executed when the
    animation finishes:
        ani.bind('on_finish', post_finish_function)

    Another optional callback is available that is called after
    each update:
        ani.bind('on_update', post_update_function)

    Animations must be added to a sprite group in order for them
    to be updated.  If the sprite group that contains them is
    drawn, then an exception will be raised, so you should create
    a sprite group only for containing Animations.

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
    """
    default_transition = 'out_quad'
    __events__= ('on_start', 'on_update', 'on_finish')

    def __init__(self, **kwargs):
        # prevent bugs if developer reuses the kwargs dict when
        # building a collection of animations
        kwargs = kwargs.copy()

        self.targets = None
        self._state = ANIMATION_NOT_STARTED
        self._elapsed = 0.
        self._delay = kwargs.get('delay', 0.)
        self._duration = float(kwargs.get('duration', 1.))
        self._initial = kwargs.get('initial', None)
        self._round_values = kwargs.get('round_values', False)
        self._transition = kwargs.get('transition', self.default_transition)
        if kwargs.get('relative', False):
            kwargs['_relative'] = True
        if isinstance(self._transition, str):
            self._transition = getattr(AnimationTransition, self._transition)
        for key in ('duration', 'transition', 'round_values', 'delay',
                    'initial'):
            kwargs.pop(key, None)
        if len(kwargs) == 0:
            raise ValueError
        self.props = kwargs

    def _get_value(self, target, name):
        """Get value of name, even if it is callable

        :param target: object than contains attribute
        :param name: name of attribute to get value from
        :return: Any
        """
        if self._initial is None:
            attr = getattr(target, name)
            if callable(attr):
                try:
                    value = attr()
                    if value is None:
                        return 0.
                    else:
                        is_number(value)
                        return value

                except TypeError:
                    # TypeError will be raised if called without needed
                    # arguments.  That is fine here, so just return 0
                    return 0.

            else:
                value = getattr(target, name)
                is_number(value)
                return value
        else:
            if callable(self._initial):
                value = self._initial()
                is_number(value)
                return value
            else:
                return self._initial

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

        :param dt: Time passed since last update.
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        self._elapsed += dt
        if self._delay > 0:
            if self._elapsed < self._delay:
                return
            else:
                self._elapsed -= self._delay
                self._delay = 0.
                return

        p = min(1., self._elapsed / self._duration)
        t = self._transition(p)
        for target, props in self.targets:
            for name, values in props.items():
                a, b = values
                value = (a * (1. - t)) + (b * t)
                self._set_value(target, name, value)

        self.broadcast('on_update')
        if p >= 1:
            self.finish()

    def finish(self):
        """Force the animation to finish

        The callbck will be called here.
        The update callback will also be called here.

        Final values will be applied

        :return: None
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        if self.targets is not None:
            for target, props in self.targets:
                for name, values in props.items():
                    a, b = values
                    self._set_value(target, name, b)

        self.broadcast('on_update')
        self._state = ANIMATION_FINISHED
        self.broadcast('on_finish')

    def abort(self):
        """Force animation state to finish

        Callbacks will not be handled and final values will not
        be applied.  It is totally fine to not call abort() if
        an animation is stopped, but if game logic requires
        animation callbacks, then this should be used.

        :return: None
        """
        if self._state is not ANIMATION_RUNNING:
            raise RuntimeError

        self._state = ANIMATION_FINISHED
        self.broadcast('on_finish')

    def start(self, target):
        """Start the animation on a target sprite/object

        Target must have the attributes that were set when
        this animation was created.

        :param target: Any valid python object
        """
        # TODO: multiple targets
        # TODO: weakref the targets
        if self._state is not ANIMATION_NOT_STARTED:
            raise RuntimeError

        self._state = ANIMATION_RUNNING
        self.targets = [(target, dict())]
        for target_, props in self.targets:
            relative = props.get('_relative', False)
            for name, value in self.props.items():
                initial = self._get_value(target_, name)
                is_number(initial)
                is_number(value)
                if relative:
                    value += initial
                props[name] = initial, value

        self.broadcast('on_start')


class AnimationTransition:
    """Collection of animation functions to be used with the Animation object.
    Easing Functions ported from Kivy and the Clutter Project
    http://www.clutter-project.org/docs/clutter/stable/ClutterAlpha.html

    The `progress` parameter in each animation function is in the range 0-1.
    """

    @staticmethod
    def linear(progress):
        """.. image:: images/anim_linear.png"""
        return progress

    @staticmethod
    def in_quad(progress):
        """.. image:: images/anim_in_quad.png
        """
        return progress * progress

    @staticmethod
    def out_quad(progress):
        """.. image:: images/anim_out_quad.png
        """
        return -1.0 * progress * (progress - 2.0)

    @staticmethod
    def in_out_quad(progress):
        """.. image:: images/anim_in_out_quad.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p
        p -= 1.0
        return -0.5 * (p * (p - 2.0) - 1.0)

    @staticmethod
    def in_cubic(progress):
        """.. image:: images/anim_in_cubic.png
        """
        return progress * progress * progress

    @staticmethod
    def out_cubic(progress):
        """.. image:: images/anim_out_cubic.png
        """
        p = progress - 1.0
        return p * p * p + 1.0

    @staticmethod
    def in_out_cubic(progress):
        """.. image:: images/anim_in_out_cubic.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p
        p -= 2
        return 0.5 * (p * p * p + 2.0)

    @staticmethod
    def in_quart(progress):
        """.. image:: images/anim_in_quart.png
        """
        return progress * progress * progress * progress

    @staticmethod
    def out_quart(progress):
        """.. image:: images/anim_out_quart.png
        """
        p = progress - 1.0
        return -1.0 * (p * p * p * p - 1.0)

    @staticmethod
    def in_out_quart(progress):
        """.. image:: images/anim_in_out_quart.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p
        p -= 2
        return -0.5 * (p * p * p * p - 2.0)

    @staticmethod
    def in_quint(progress):
        """.. image:: images/anim_in_quint.png
        """
        return progress * progress * progress * progress * progress

    @staticmethod
    def out_quint(progress):
        """.. image:: images/anim_out_quint.png
        """
        p = progress - 1.0
        return p * p * p * p * p + 1.0

    @staticmethod
    def in_out_quint(progress):
        """.. image:: images/anim_in_out_quint.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p * p
        p -= 2.0
        return 0.5 * (p * p * p * p * p + 2.0)

    @staticmethod
    def in_sine(progress):
        """.. image:: images/anim_in_sine.png
        """
        return -1.0 * cos(progress * (pi / 2.0)) + 1.0

    @staticmethod
    def out_sine(progress):
        """.. image:: images/anim_out_sine.png
        """
        return sin(progress * (pi / 2.0))

    @staticmethod
    def in_out_sine(progress):
        """.. image:: images/anim_in_out_sine.png
        """
        return -0.5 * (cos(pi * progress) - 1.0)

    @staticmethod
    def in_expo(progress):
        """.. image:: images/anim_in_expo.png
        """
        if progress == 0:
            return 0.0
        return pow(2, 10 * (progress - 1.0))

    @staticmethod
    def out_expo(progress):
        """.. image:: images/anim_out_expo.png
        """
        if progress == 1.0:
            return 1.0
        return -pow(2, -10 * progress) + 1.0

    @staticmethod
    def in_out_expo(progress):
        """.. image:: images/anim_in_out_expo.png
        """
        if progress == 0:
            return 0.0
        if progress == 1.:
            return 1.0
        p = progress * 2
        if p < 1:
            return 0.5 * pow(2, 10 * (p - 1.0))
        p -= 1.0
        return 0.5 * (-pow(2, -10 * p) + 2.0)

    @staticmethod
    def in_circ(progress):
        """.. image:: images/anim_in_circ.png
        """
        return -1.0 * (sqrt(1.0 - progress * progress) - 1.0)

    @staticmethod
    def out_circ(progress):
        """.. image:: images/anim_out_circ.png
        """
        p = progress - 1.0
        return sqrt(1.0 - p * p)

    @staticmethod
    def in_out_circ(progress):
        """.. image:: images/anim_in_out_circ.png
        """
        p = progress * 2
        if p < 1:
            return -0.5 * (sqrt(1.0 - p * p) - 1.0)
        p -= 2.0
        return 0.5 * (sqrt(1.0 - p * p) + 1.0)

    @staticmethod
    def in_elastic(progress):
        """.. image:: images/anim_in_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        q -= 1.0
        return -(pow(2, 10 * q) * sin((q - s) * (2 * pi) / p))

    @staticmethod
    def out_elastic(progress):
        """.. image:: images/anim_out_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        return pow(2, -10 * q) * sin((q - s) * (2 * pi) / p) + 1.0

    @staticmethod
    def in_out_elastic(progress):
        """.. image:: images/anim_in_out_elastic.png
        """
        p = .3 * 1.5
        s = p / 4.0
        q = progress * 2
        if q == 2:
            return 1.0
        if q < 1:
            q -= 1.0
            return -.5 * (pow(2, 10 * q) * sin((q - s) * (2.0 * pi) / p))
        else:
            q -= 1.0
            return pow(2, -10 * q) * sin((q - s) * (2.0 * pi) / p) * .5 + 1.0

    @staticmethod
    def in_back(progress):
        """.. image:: images/anim_in_back.png
        """
        return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)

    @staticmethod
    def out_back(progress):
        """.. image:: images/anim_out_back.png
        """
        p = progress - 1.0
        return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0

    @staticmethod
    def in_out_back(progress):
        """.. image:: images/anim_in_out_back.png
        """
        p = progress * 2.
        s = 1.70158 * 1.525
        if p < 1:
            return 0.5 * (p * p * ((s + 1.0) * p - s))
        p -= 2.0
        return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)

    @staticmethod
    def _out_bounce_internal(t, d):
        p = t / d
        if p < (1.0 / 2.75):
            return 7.5625 * p * p
        elif p < (2.0 / 2.75):
            p -= (1.5 / 2.75)
            return 7.5625 * p * p + .75
        elif p < (2.5 / 2.75):
            p -= (2.25 / 2.75)
            return 7.5625 * p * p + .9375
        else:
            p -= (2.625 / 2.75)
            return 7.5625 * p * p + .984375

    @staticmethod
    def _in_bounce_internal(t, d):
        return 1.0 - AnimationTransition._out_bounce_internal(d - t, d)

    @staticmethod
    def in_bounce(progress):
        """.. image:: images/anim_in_bounce.png
        """
        return AnimationTransition._in_bounce_internal(progress, 1.)

    @staticmethod
    def out_bounce(progress):
        """.. image:: images/anim_out_bounce.png
        """
        return AnimationTransition._out_bounce_internal(progress, 1.)

    @staticmethod
    def in_out_bounce(progress):
        """.. image:: images/anim_in_out_bounce.png
        """
        p = progress * 2.
        if p < 1.:
            return AnimationTransition._in_bounce_internal(p, 1.) * .5
        return AnimationTransition._out_bounce_internal(p - 1., 1.) * .5 + .5

