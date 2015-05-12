from math import sqrt, cos, sin, pi

__all__ = ('AnimationTransition', )


class AnimationTransition(object):
    """Collection of animation functions to be used with the Animation object.
    Easing Functions ported to Kivy from the Clutter Project
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
