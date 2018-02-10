import toga
from toga.style.pack import *
import os
import map_from_file


def button_handler(widget):
    print("hello")


class Map(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(self.name)
        url = "file:///" + os.path.abspath("Map.html")
        self.webview = toga.WebView(style=Pack(flex=1,
                                               padding_left=80,
                                               padding_top=100))
        box = toga.Box(
            children=[
                toga.Box(
                    children=[],
                    style=Pack(
                        direction=ROW
                    )
                ),
                self.webview,
            ],
            style=Pack(
                direction=COLUMN
            )
        )

        self.main_window.content = box
        self.webview.url = url

        self.main_window.show()


def create_map_window(year):
    map_from_file.create_map(year)
    window = Map("Map", "ua.in.ucu.map")
    window.main_loop()


def build(app):
    box = toga.Box()
    sen_box = toga.Box()
    year_box = toga.Box()
    button_box = toga.Box()

    sen_label = toga.Label("Write year in which film was made",
                           style=Pack(text_align=CENTER))
    year_input = toga.TextInput()

    def find_films(widget):
        try:
            year = int(year_input.value)
            if year < 0:
                raise ValueError
        except ValueError:
            year_input.value = "Invalid year"
        else:
            create_map_window(year)

    result_button = toga.Button("Confirm", on_press=find_films)

    sen_box.add(sen_label)
    year_box.add(year_input)
    button_box.add(result_button)

    box.add(sen_box)
    box.add(year_box)
    box.add(button_box)

    box.style.update(direction=COLUMN, padding_top=50)
    sen_label.style.update(width=400, padding_top=50, padding_left=100)
    year_input.style.update(width=200, text_align=RIGHT, padding_left=200)
    button_box.style.update(text_align=CENTER, padding_left=270)
    return box


def main():
    return toga.App('Choose year app', 'ua.in.ucu.start', startup=build)


if __name__ == '__main__':
    main().main_loop()
