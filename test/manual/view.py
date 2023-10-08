from pathlib import Path
from tkinter import Tk, PhotoImage, StringVar
from tkinter.ttk import Frame, Button, Label

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
    def __init__(self, master: Tk):
        super().__init__(master)
        self.grid(
            row=0, column=0,
            sticky='nsew',
            padx=20, pady=20,
        )
        self.rowconfigure(0, minsize=175)
        self.rowconfigure(1, minsize=560)
        self.rowconfigure(2, minsize=85)
        self.columnconfigure(0, minsize=560)

        text_panel = Frame(self)
        text_panel.grid(
            row=0, column=0,
            sticky='nsew',
            pady=(0, 20),
        )
        text_panel.rowconfigure(0, minsize=175)
        text_panel.columnconfigure(0, minsize=400)
        text_panel.columnconfigure(1, minsize=160)

        self.message = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.message,
            wraplength=400,
            font=('Enceladus', 22, 'italic'),
            anchor='nw',
            justify='left',
            # background='#ccc',
        ).grid(
            row=0, column=0,
            sticky='nsew',
            ipadx=5, ipady=5,
        )

        self.params = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.params,
            wraplength=160,
            font=('Candara', 20, 'bold'),
            anchor='ne',
            justify='right',
            # background='#ddd',
        ).grid(
            row=0, column=1,
            sticky='nsew',
            ipadx=5, ipady=5,
        )

        self._image: PhotoImage = None
        self.screen = Label(self)
        self.screen.grid(
            row=1, column=0,
            sticky='nsew',
            pady=(0, 20),
        )

        buttons_panel = Frame(self)
        buttons_panel.grid(
            row=2, column=0,
            sticky='nsew',
        )

        self.actions: list[Button] = []
        self._buttons_images: list[PhotoImage] = []
        paddings = (11, 11, 11, 11, 11, 0)
        for i, pad in enumerate(paddings):
            self._buttons_images.append(PhotoImage(file=fr'd:\G-Doc\TOP Academy\Python web\321\projects\2\_ref\data\images\btn{i+1}.png'))
            btn = Button(
                buttons_panel,
                image=self._buttons_images[-1],
                # command=,
            )
            btn.grid(
                row=0, column=i,
                sticky='nsew',
                padx=(0, pad),
            )
            self.actions.append(btn)

    def change_message(self, text: str) -> None:
        self.message.set(text)
        self.update_idletasks()

    def change_params(self, text: str) -> None:
        self.params.set(text)
        self.update_idletasks()

    def change_image(self, img_path: str | Path) -> None:
        self._image = PhotoImage(
            width=560, height=560,
            file=img_path,
        )
        # self.screen['image'] = self._image
        # self.screen.config(image=self._image)
        self.screen.configure(image=self._image)
        self.update_idletasks()


if __name__ == '__main__':
    root = RootWidget()

    # root.mainframe = MainMenu(root, controller.loaded_kinds)

    root.mainframe = Game(root)
    root.mainframe.change_message('test message\nтестовое сообщение')
    root.mainframe.change_params('health: 20\nсытость: 15')
    root.mainframe.change_image(r'd:\G-Doc\TOP Academy\Python web\321\projects\2\_ref\doc\.img_refs\dogs2.png')

    root.mainloop()

