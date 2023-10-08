from tkinter import Tk, PhotoImage
from tkinter.ttk import Frame, Button

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


class MainMenu(Frame):
    """"""
    def __init__(self, master: Tk, kinds: controller.LoadKinds[model.Kind]):
        super().__init__(master)
        self.grid(
            row=0, column=0,
            padx=10, pady=10,
            sticky='nsew',
        )
        columns = 2
        self._images: list[PhotoImage] = []
        for i, kind in enumerate(kinds):
            self._images.append(PhotoImage(
                file=kind.image,
                width=260, height=260
            ))
            row, column = divmod(i, columns)
            Button(
                self,
                image=self._images[i],
                # command=,
            ).grid(
                row=row, column=column,
                sticky='nsew',
                padx=10, pady=10,
            )


class Game(Frame):
    """"""


if __name__ == '__main__':
    root = RootWidget()

    root.mainframe = MainMenu(root, controller.loaded_kinds)

    root.mainloop()

