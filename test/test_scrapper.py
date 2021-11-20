import unittest

from bot.scrapper import MenuItem, Olivka


class RenderMenu(unittest.TestCase):
    def test_empty(self):
        self.assertEqual('Увы на сегодня ничего :(', Olivka.render_menu('FOO', [], 20))

    def test_simple(self):
        expected = ('+====== FOO =======+\n'
                    '| FooBar           |\n'
                    '+------------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', None, None)], 20))

    def test_low_width1(self):
        expected = ('+= FOO ==+\n'
                    '| FooBar |\n'
                    '+--------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', None, None)], 10))

    def test_bad_header(self):
        with self.assertRaises(ValueError):
            Olivka.render_menu('FOO', [MenuItem('FooBar', None, None)], 5)

    def test_bad_width(self):
        with self.assertRaises(ValueError):
            Olivka.render_menu('FOO', [MenuItem('FooBar', None, None)], 4)

    def test_portion(self):
        expected = ('+====== FOO =======+\n'
                    '| FooBar [portion] |\n'
                    '+------------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', 'portion', None)], 20))

    def test_info(self):
        expected = ('+====== FOO =======+\n'
                    '| FooBar (info)    |\n'
                    '+------------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', None, 'info')], 20))

    def test_portion_and_info(self):
        expected = ('+========== FOO ==========+\n'
                    '| FooBar [portion] (info) |\n'
                    '+-------------------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', 'portion', 'info')], 27))

    def test_wrap(self):
        expected = ('+==== FOO ====+\n'
                    '| FooBar      |\n'
                    '| [portion]   |\n'
                    '| (info)      |\n'
                    '+-------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', [MenuItem('FooBar', 'portion', 'info')], 15))

    def test_multiple_items(self):
        items = [MenuItem('Foo', None, None), MenuItem('Bar', None, None), MenuItem('Baz', None, None)]
        expected = ('+==== FOO ====+\n'
                    '| Foo         |\n'
                    '+-------------+\n'
                    '| Bar         |\n'
                    '+-------------+\n'
                    '| Baz         |\n'
                    '+-------------+')
        self.assertEqual(expected, Olivka.render_menu('FOO', items, 15))
