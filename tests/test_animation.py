from unittest import TestCase

from pygame.sprite import Group
from mock import Mock

from pygameanimation import Animation, Task, remove_animations_of
from pygameanimation.animation import is_number


class TestObject:
    """ Mocks don't work well with animations due to introspection,
    so this is to be used instead of a mock.
    """

    def __init__(self):
        self.value = 0.0
        self.illegal_value = 'spam'
        self.callable = Mock(return_value=0)
        self.initial = 0.0

    def set_value(self, value):
        self.value = value

    def get_initial(self):
        return self.initial

    def get_illegal_value(self):
        return self.illegal_value


class TestAnimation(TestCase):
    def setUp(self):
        self.mock = TestObject()

    def test_is_number_int(self):
        self.assertTrue(is_number(1))
        self.assertTrue(is_number('1'))

    def test_is_number_float(self):
        self.assertTrue(is_number(1.5))
        self.assertTrue(is_number('1.5'))

    def test_is_number_non_number_raises_ValueError(self):
        with self.assertRaises(ValueError):
            is_number('abc')

        with self.assertRaises(ValueError):
            is_number((1, 2, 3))

    def simulate(self, animation, times=100):
        """ used to simulate a clock updating the animation for some time
        default is one second
        """
        for time in range(times):
            animation.update(.01)

    def test_can_add_to_group(self):
        a = Animation(value=1)
        g = Group(a)

    def test_finished_removes_from_group(self):
        a = Animation(value=1)
        g = Group(a)
        a.start(self.mock)
        a.finish()
        self.assertNotIn(a, g)

    def test_aborted_removes_from_group(self):
        a = Animation(value=1)
        g = Group(a)
        a.start(self.mock)
        a.abort()
        self.assertNotIn(a, g)

    def test_remove_animations_of(self):
        m0, m1 = TestObject(), TestObject()
        a0 = Animation(value=1)
        a0.start(m0)
        a1 = Animation(value=1)
        a1.start(m1)
        g = Group(a0, a1)
        self.assertEqual(len(g), 2)

        remove_animations_of(g, m0)
        self.assertEqual(len(g), 1)
        self.assertIn(a1, g)
        self.assertNotIn(a0, g)

        remove_animations_of(g, m1)
        self.assertEqual(len(g), 0)
        self.assertNotIn(a1, g)

    def test_round_values(self):
        """ verify that values are rounded to the nearest whole integer
        """
        a = Animation(value=1.1, round_values=True, duration=1)
        a.start(self.mock)

        # verify that it rounds down (.25 => 0)
        self.simulate(a, 25)
        self.assertEqual(self.mock.value, 0)

        # verify that it rounds up (.75 => 1)
        self.simulate(a, 50)
        self.assertEqual(self.mock.value, 1)

        # verify that final value is also rounded
        self.simulate(a, 25)
        self.assertEqual(self.mock.value, 1)

    def test_relative_values(self):
        a = Animation(value=1)
        self.mock.value = 1
        a.start(self.mock, relative=True)
        a.finish()
        self.assertEqual(self.mock.value, 2)

    def test_start_will_not_set_values(self):
        """ verify that the animation will not change values at start
        """
        a = Animation(value=1)
        a.start(self.mock)
        self.assertEqual(self.mock.value, 0)

    def test_update_attribute(self):
        """ verify that the animation can modify normal attributes
        """
        a = Animation(value=1, duration=1)
        a.start(self.mock)
        a.update(1)
        self.assertEqual(self.mock.value, 1)

    def test_target_callable(self):
        """ verify that the animation will update callable attributes
        """
        a = Animation(callable=1, duration=2)
        a.start(self.mock)

        # callable will be called because it is being checked for a value.
        # this check can be bypassed by passing an initial value
        self.assertEqual(self.mock.callable.call_count, 1)
        self.assertEqual(self.mock.callable.call_args[0], ())

        # simulate passage of 1 second time
        a.update(1)
        self.assertEqual(self.mock.callable.call_count, 2)
        # .5 value is derived from: time elapsed (1) / duration (2)
        self.assertEqual(self.mock.callable.call_args[0], (.5, ))

    def test_target_callable_with_initial(self):
        """ verify that the animation will update callable attributes
        """
        a = Animation(callable=1, initial=0, duration=2)
        a.start(self.mock)

        # callable should not be checked because the initial is passed
        self.assertFalse(self.mock.callable.called)

        # simulate passage of 1 second time
        a.update(1)
        self.assertEqual(self.mock.callable.call_count, 1)
        # .5 value is derived from: time elapsed (1) / duration (2)
        self.assertEqual(self.mock.callable.call_args[0], (.5, ))

    def test_set_initial(self):
        """ verify that the animation will set initial values
        """
        a = Animation(value=1, initial=.5)
        a.start(self.mock)

        # this will set the value to the initial
        a.update(0)
        self.assertEqual(self.mock.value, .5)

    def test_set_initial_callable(self):
        """ verify that the animation will set initial values from a callable
        """
        a = Animation(value=1, initial=self.mock.get_initial)
        a.start(self.mock)

        # this will set the value to the initial
        a.update(0)
        self.assertEqual(self.mock.value, self.mock.initial)

    def test_delay(self):
        """ verify that this will not start until the delay
        """
        a = Animation(value=1, delay=1, duration=1)
        a.start(self.mock)

        self.simulate(a, 100)
        self.assertEqual(self.mock.value, 0)

        self.simulate(a, 100)
        self.assertEqual(self.mock.value, 1)

    def test_finish_before_complete(self):
        """ verify that calling finish before complete will set final values
        """
        a = Animation(value=1)
        a.start(self.mock)
        a.finish()
        self.assertEqual(self.mock.value, 1)

    def test_update_callback_called(self):
        """ verify that update_callback is called each update and final
        """
        m = Mock()
        a = Animation(value=1, duration=1)
        a.update_callback = m
        a.start(self.mock)
        self.simulate(a)
        self.assertTrue(m.called)

        # 101 = 100 iterations of update + 1 iteration during the finalizer
        self.assertEqual(m.call_count, 101)

    def test_final_callback_called_when_finished(self):
        """ verify that callback is called during the finalizer when finishes
        """
        m = Mock()
        a = Animation(value=1, duration=1)
        a.callback = m
        a.start(self.mock)
        self.simulate(a)
        self.assertTrue(m.called)
        self.assertEqual(m.call_count, 1)

    def test_final_callback_called_when_aborted(self):
        """ verify that callback is called during the finalizer when aborted
        """
        m = Mock()
        a = Animation(value=1)
        a.callback = m
        a.start(self.mock)
        a.abort()
        self.assertTrue(m.called)
        self.assertEqual(m.call_count, 1)

    def test_update_callback_not_called_when_aborted(self):
        m = Mock()
        a = Animation(value=1)
        a.update_callback = m
        a.start(self.mock)
        a.abort()
        self.assertFalse(m.called)

    def test_values_not_applied_when_aborted(self):
        a = Animation(value=1)
        a.start(self.mock)
        a.abort()
        self.assertEqual(self.mock.value, 0)

    def test_update_callable_with_initial(self):
        a = Animation(callable=1, duration=1, initial=0)
        a.start(self.mock)
        a.update(1)
        # call #1 is update, call #2 is finalizer
        self.assertEqual(self.mock.callable.call_count, 2)

    def test_get_value_attribute(self):
        """ Verify getter properly handles attribute
        """
        a = Animation(value=1)
        self.assertEqual(a._get_value(self.mock, 'value'), 0)

    def test_get_value_callable_attribute(self):
        """ Verify getter properly handles callable attribute
        """
        assert (callable(self.mock.callable))
        a = Animation(callable=1)
        self.assertEqual(a._get_value(self.mock, 'callable'), 0)

    def test_get_value_initial(self):
        """ Verify getter properly handles initial attribute
        """
        a = Animation(value=1, initial=0)
        self.assertEqual(a._get_value(None, None), 0)

    def test_get_value_initial_callable(self):
        """ Verify getter properly handles callable initial attribute
        """
        a = Animation(value=1, initial=self.mock.callable)
        self.assertEqual(a._get_value(None, 'value'), 0)

    def test_set_value_attribute(self):
        """ Verify setter properly handles attribute
        """
        a = Animation(value=1)
        a._set_value(self.mock, 'value', 10)
        self.assertEqual(self.mock.value, 10)

    def test_set_value_callable_attribute(self):
        """ Verify setter properly handles callable attribute
        """
        a = Animation(value=1)
        a._set_value(self.mock, 'callable', 0)
        self.assertTrue(self.mock.callable.called)
        self.assertEqual(self.mock.callable.call_count, 1)
        self.assertEqual(self.mock.callable.call_args[0], (0, ))

    def test_non_number_target_raises_valueerror(self):
        a = Animation(value=self.mock.illegal_value)
        with self.assertRaises(ValueError):
            a.start(self.mock)

        a = Animation(value=self.mock.get_illegal_value)
        with self.assertRaises(ValueError):
            a.start(self.mock)

    def test_non_number_initial_raises_valueerror(self):
        a = Animation(illegal_value=1)
        with self.assertRaises(ValueError):
            a.start(self.mock)

        a = Animation(value=1, initial=self.mock.get_illegal_value)
        with self.assertRaises(ValueError):
            a.start(self.mock)

    def test_no_targets_raises_valueerror(self):
        with self.assertRaises(ValueError):
            Animation()

    def test_abort_before_start_raises_runtimeerror(self):
        a = Animation(value=1)

        with self.assertRaises(RuntimeError):
            a.abort()

    def test_finish_before_start_raises_runtimeerror(self):
        a = Animation(value=1)

        with self.assertRaises(RuntimeError):
            a.finish()

    def test_exceed_duration_raises_runtimeerror(self):
        a = Animation(value=1, duration=1)
        a.start(self.mock)

        with self.assertRaises(RuntimeError):
            self.simulate(a, 101)

    def test_finish_then_update_raises_runtimeerror(self):
        a = Animation(value=1)
        a.start(self.mock)
        a.finish()

        with self.assertRaises(RuntimeError):
            a.update(1)

    def test_finish_then_start_raises_runtimeerror(self):
        a = Animation(value=1)
        a.start(self.mock)
        a.finish()

        with self.assertRaises(RuntimeError):
            a.start(None)

    def test_finish_twice_raises_runtimeerror(self):
        a = Animation(value=1)
        a.start(self.mock)
        a.finish()

        with self.assertRaises(RuntimeError):
            a.finish()

    def test_start_twice_raises_runtimeerror(self):
        a = Animation(value=1)
        a.start(self.mock)

        with self.assertRaises(RuntimeError):
            a.start(None)


class TestTask(TestCase):
    def simulate(self, object_, duration=1, step=1):
        """ used to simulate a clock updating something for some time
        default is one second
        """
        elapsed = 0
        while elapsed < duration:
            elapsed += step
            object_.update(step)

    def test_not_callable_rases_AssertionError(self):
        with self.assertRaises(ValueError):
            Task(None)

    def test_zero_or_negative_loops_reaises_AssertionError(self):
        with self.assertRaises(ValueError):
            Task(Mock(), loops=0)

        with self.assertRaises(ValueError):
            Task(Mock(), loops=-1)

    def test_update_once(self):
        m = Mock()
        t = Task(m, interval=1)
        t.update(1)
        self.assertEqual(m.call_count, 1)

    def test_update_many(self):
        m = Mock()
        t = Task(m, interval=1, loops=10)
        self.simulate(t, 10)
        self.assertEqual(m.call_count, 10)

    def test_abort_does_not_callback(self):
        m = Mock()
        t = Task(m, interval=0)
        t.abort()
        self.assertEqual(m.call_count, 0)

    def test_chain(self):
        m0, m1 = Mock(), Mock()
        t0 = Task(m0, interval=0)
        t1 = t0.chain(Task(m1, interval=0))
        g = Group(t0)
        # sanity
        self.assertNotIn(t1, g)

        # this update will cause the chain to execute
        # it will also add chained Tasks to the group
        g.update(1)
        self.assertTrue(m0.called)
        self.assertIn(t1, g)

        # this update will now cause the chained Task to complete
        g.update(1)
        self.assertTrue(m1.called)

    def test_update_over_duration_raises_RuntimeError(self):
        m = Mock()
        t = Task(m, interval=1)
        with self.assertRaises(RuntimeError):
            self.simulate(t, 10)

    def test_update_after_abort_raises_RuntimeError(self):
        t = Task(Mock(), interval=1)
        t.abort()
        with self.assertRaises(RuntimeError):
            t.update(1)

    def test_chain_non_Task_raises_TypeError(self):
        with self.assertRaises(TypeError):
            Task(Mock()).chain(None)
