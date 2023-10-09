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

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.width = screen_width // 3
        self.height = screen_height * 3 // 4
        x = screen_width // 2 - self.width // 2
        y = screen_height // 2 - self.height // 2

        self.geometry(f'{self.width}x{self.height}+{x}+{y}')
        self.resizable(False, False)

        self.mainframe: Frame = None

    def change_frame(self, new_frame: Frame):
        self.mainframe.destroy()
        self.mainframe = new_frame
        self.update()


class MainMenu(Frame):
    """"""
    def __init__(self, master: RootWidget, kinds: controller.LoadKinds[model.Kind]):
        super().__init__(master)
        pad = master.width // 100 + 1
        self.grid(
            row=0, column=0,
            padx=pad, pady=pad,
            sticky='nsew',
        )
        columns = 2
        img_size = (master.width - pad*2*(columns+1)) // columns - 10
        self._images: list[PhotoImage] = []
        for i, kind in enumerate(kinds):
            self._images.append(PhotoImage(
                width=img_size, height=img_size,
                file=kind.image,
            ))
            row, column = divmod(i, columns)
            btn = Button(
                self,
                image=self._images[i],
                # для теста:
                command=lambda: master.change_frame(Game(master, yara)),
                # на перспективу:
                # command=lambda: master.change_frame(Game(master, controller.MainMenu.choose_kind(kind))),
            )
            btn.grid(
                row=row, column=column,
                sticky='nsew',
                padx=pad, pady=pad,
            )

class Game(Frame):
    """"""
    def __init__(self, master: RootWidget, origin: model.Creature):
        super().__init__(master)
        pad = (master.width // 100 + 1) * 2
        ipad = pad // 4
        self.grid(
            row=0, column=0,
            sticky='nsew',
            padx=pad, pady=pad,
        )
        self._screen_size = master.width - pad * 2
        self._actions_height = (master.height - self._screen_size - pad*4) // 3
        self._text_height = self._actions_height * 2
        self.rowconfigure(0, minsize=self._text_height)
        self.rowconfigure(1, minsize=self._screen_size)
        self.rowconfigure(2, minsize=self._actions_height)
        self.columnconfigure(0, minsize=self._screen_size)

        text_panel = Frame(self)
        text_panel.grid(
            row=0, column=0,
            sticky='nsew',
            pady=(0, pad),
        )
        text_panel.rowconfigure(0, minsize=self._text_height)
        text_panel.columnconfigure(0, minsize=self._screen_size//7*5)
        text_panel.columnconfigure(1, minsize=self._screen_size//7*2)

        self.message = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.message,
            wraplength=self._screen_size//7*5,
            font=('Arial Narrow', 16, 'italic'),
            anchor='nw',
            justify='left',
            # background='#ccc',
        ).grid(
            row=0, column=0,
            sticky='nsew',
            ipadx=ipad, ipady=ipad,
        )

        self.params = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.params,
            wraplength=self._screen_size//7*2,
            font=('Consolas', 16, 'bold'),
            anchor='ne',
            justify='right',
            # background='#ddd',
        ).grid(
            row=0, column=1,
            sticky='nsew',
            ipadx=ipad, ipady=ipad,
        )

        self._image: PhotoImage = None
        self.screen = Label(self)
        self.screen.grid(
            row=1, column=0,
            sticky='nsew',
            pady=(0, pad),
        )

        self.create_buttons(origin)

    def create_buttons(self, origin: model.Creature):
        buttons_panel = Frame(self)
        buttons_panel.grid(
            row=2, column=0,
            sticky='nsew',
        )
        buttons = 6
        self.actions: list[Button] = []
        self._buttons_images: list[PhotoImage] = []
        paddings = ((self._screen_size - self._actions_height*6)//(buttons-1),)*(buttons-1) + (0,)
        img_size = self._actions_height - 10
        for i, pad in enumerate(paddings):
            try:
                action = origin.player_actions[i]
            except IndexError:
                action = model.NoAction()
            self._buttons_images.append(PhotoImage(
                width=img_size, height=img_size,
                file=action.image
            ))
            btn = Button(
                buttons_panel,
                image=self._buttons_images[-1],
                state=action.state,
                # необходимо добавить параметр в lambda-функцию, чтобы каждая из создаваемых в цикле функций обращалась к соответствующему экземпляру action
                # иначе, функции обращаются к action только во время вызова, а не в момент создания
                # https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
                command=lambda act=action: self.change_message(f'{act}\n{act.action()}'),
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
            width=self._screen_size, height=self._screen_size,
            file=img_path,
        )
        self.screen.configure(image=self._image)
        self.update_idletasks()

    def update_creature(self, origin: model.Creature):
        origin.update()
        self.change_params(repr(origin))
        self.after(1000, lambda: self.update_creature(origin))
        self.update()



if __name__ == '__main__':
    root = RootWidget()

    # root.mainframe = MainMenu(root, controller.loaded_kinds)

    yara = model.Creature(model.cat_kind, 'Яра')
    root.mainframe = Game(root, yara)
    root.mainframe.change_message('\n'.join(str(act) for act in yara.player_actions))
    root.mainframe.change_image(r'd:\G-Doc\TOP Academy\Python web\321\projects\2\_ref\doc\.img_refs\dog_1.png')
    root.mainframe.update_creature(yara)

    root.mainloop()

