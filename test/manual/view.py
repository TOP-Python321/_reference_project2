from math import ceil
from tkinter import Tk, PhotoImage
from tkinter.ttk import Frame, Button
from typing import Type

import model
import controller


class RootWidget(Tk):
    """"""
    def __init__(self):
        super().__init__()
        self.title('Тамагочи')

        width = 600
        height = 900
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

        self.mainframe: Frame = None

    def mainloop(self, n: int = 0) -> None:
        self.mainframe.grid(
            row=0, column=0,
            padx=10, pady=10,
            # ipadx=10, ipady=10,
            sticky='nsew',
        )
        super().mainloop(n)


class MainMenu(Frame):
    """"""
    def __init__(self, master: Tk, kinds: controller.LoadKinds[model.Kind]):
        super().__init__(master)
        columns = 2
        self.images: list[PhotoImage] = []
        for i, kind in enumerate(kinds):
            self.images.append(PhotoImage(file=kind.image))
            row, column = divmod(i, columns)
            Button(
                self,
                # borderwidth=0,
                image=self.images[i],
                # width=275, height=275,
                # command=,
            ).grid(
                row=row, column=column,
                sticky='nsew',
                pady=10, padx=10
            )


class Game(Frame):
    """"""


if __name__ == '__main__':
    app = RootWidget()
    app.mainframe = MainMenu(app, controller.loaded_kinds)
    app.mainloop()

