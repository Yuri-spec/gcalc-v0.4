from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import os
import kivy
kivy.require('1.11.1')


grocery_list = '/storage/emulated/0/Groceries.txt'

if (kivy.utils.platform != 'android'):
    grocery_list = os.path.join(os.environ['HOME'], 'Groceries.txt')


class Grocery:
    def __init__(self, name):
        # info
        self.name = name.title()
        self.quant = 0
        self.value = 0
        # sizes
        self.height = 100
        self.quant_size = (.3, None)
        # colors
        self.blue = (.25, .75, 1, 1)
        self.blue_ok = (.75, 1.25, 1.5, 1)
        self.red = (1, .25, .50, 1)

    def label_name(self):
        return Label(text=self.name,
                     size_hint_y=None,
                     height=self.height)

    def label_quant(self):
        return Label(text=str(self.quant),
                     size_hint=self.quant_size,
                     height=self.height)

    def btn_quant_add(self):
        def run():
            self.quant += 1
            main.screen_refresh()
        return Button(text='+',
                      size_hint=self.quant_size,
                      height=self.height,
                      on_release=lambda x: run())

    def btn_quant_rem(self):
        def run():
            self.quant -= 1
            main.screen_refresh()

        def run2():
            main.groceries.remove(self)
            main.screen_refresh()
            add.screen_refresh()

        if self.quant > 0:
            return Button(text='-',
                          size_hint=self.quant_size,
                          height=self.height,
                          on_release=lambda x: run())
        else:
            return Button(text='×',
                          size_hint=self.quant_size,
                          height=self.height,
                          background_color=self.red,
                          on_release=lambda x: run2())

    def btn_value(self):
        def run():
            calc.selected = self
            calc.ids.selected.text = self.name
            if self.value > 0:
                calc.ids.entry.hint_text = '{:,.2f}'.format(self.value)
            else:
                calc.ids.entry.hint_text = '0'
            calc.ids.entry.text = ''
            sm.transition.direction = 'left'
            sm.current = 'calc'

        if self.value > 0:
            if self.quant > 0:
                return Button(text='{:,.2f}'.format(self.value),
                              size_hint_y=None,
                              height=self.height,
                              background_color=self.blue_ok,
                              on_release=lambda x: run())
            else:
                return Button(text='{:,.2f}'.format(self.value),
                              size_hint_y=None,
                              height=self.height,
                              background_color=self.blue,
                              on_release=lambda x: run())
        else:
            return Button(text='...',
                          size_hint_y=None,
                          height=self.height,
                          background_color=self.blue,
                          on_release=lambda x: run())

    def btn_add(self):
        def run():
            main.groceries.append(self)
            main.screen_refresh()
            add.screen_refresh()

        added = [i.name for i in main.groceries]

        if self.name in added:
            return Label(text=str(self.name),
                         size_hint_y=None,
                         height=self.height * 2)
        else:
            return Button(text=str(self.name),
                          size_hint_y=None,
                          height=self.height * 2,
                          on_release=lambda x: run())


# Screens
class Groceries(Screen):
    def __init__(self, **kwargs):
        super(Groceries, self).__init__(**kwargs)
        self.groceries = []

        if os.path.exists(grocery_list):
            with open(grocery_list) as items:
                for item in items.readlines():
                    if item.strip():
                        self.groceries.append(Grocery(item.strip()))

        self.screen_refresh()

    def screen_refresh(self):
        self.ids.rows.clear_widgets()
        groceries = sorted(self.groceries, key=lambda x: x.name)
        total_value = 0

        for grocery in groceries:
            self.ids.rows.add_widget(grocery.label_name())
            self.ids.rows.add_widget(grocery.btn_quant_rem())
            self.ids.rows.add_widget(grocery.label_quant())
            self.ids.rows.add_widget(grocery.btn_quant_add())
            self.ids.rows.add_widget(grocery.btn_value())
            total_value += grocery.quant * grocery.value

        self.ids.total_value.text = '{:,.2f}'.format(total_value)


class AddItems(Screen):
    def __init__(self, **kwargs):
        super(AddItems, self).__init__(**kwargs)
        self.frequent = [  # Insert frequently bought items here
            'Beans', 'Biscuits', 'Butter', 'Coffee', 'Cornstarch', 'Eggs', 'Flour',
            'Fruit', 'Meat', 'Milk', 'Oil', 'Rice', 'Salt', 'Pasta',
            'Sugar', 'Toilet Paper', 'Tomato Sauce', 'Toothpaste', 'Vegetables', 'Yeast',
        ]

        self.screen_refresh()

    def screen_refresh(self):
        self.ids.frequent.clear_widgets()

        for item in self.frequent:
            self.ids.frequent.add_widget(Grocery(item).btn_add())

    entry = ObjectProperty(None)

    def btn(self):
        entry = self.entry.text

        if entry.strip():
            main.groceries.append(Grocery(entry))
            self.screen_refresh()
            main.screen_refresh()
            sm.transition.direction = 'left'
            sm.current = 'main'


class Calculator(Screen):
    selected = ''
    entry = ObjectProperty(None)

    def btn(self):
        entry = self.entry.text

        # return value if not a dot or blank; 0 otherwise
        if entry.strip():
            if entry != '.':
                self.selected.value = float(entry)
            else:
                self.selected.value = 0
        else:
            self.selected.value = 0

        # auto adjust quant to match value if necessary
        if self.selected.value > 0:
            if self.selected.quant < 1:
                self.selected.quant = 1
        else:
            self.selected.quant = 0

        main.screen_refresh()


kv = Builder.load_file('my.kv')

# Screens
sm = ScreenManager()
main = Groceries(name='main')
add = AddItems(name='add')
calc = Calculator(name='calc')


class GCalc(App):
    def build(self):
        sm.add_widget(main)
        sm.add_widget(add)
        sm.add_widget(calc)
        if not main.groceries:
            sm.current = 'add'
        return sm


if __name__ == '__main__':
    GCalc().run()
