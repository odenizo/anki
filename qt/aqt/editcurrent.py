# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from __future__ import annotations

from collections.abc import Callable

import aqt.editor
from anki.collection import OpChanges
from anki.errors import NotFoundError
from aqt import gui_hooks
from aqt.qt import *
from aqt.utils import add_close_shortcut, restoreGeom, saveGeom, tr


class EditCurrent(QMainWindow):
    def __init__(self, mw: aqt.AnkiQt) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self.mw = mw
        self.form = aqt.forms.editcurrent.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle(tr.editing_edit_current())
        self.setMinimumHeight(400)
        self.setMinimumWidth(250)
        if not is_mac:
            self.setMenuBar(None)
        self.editor = aqt.editor.Editor(
            self.mw,
            self.form.fieldsArea,
            self,
            editor_mode=aqt.editor.EditorMode.EDIT_CURRENT,
        )
        assert self.mw.reviewer.card is not None
        self.editor.card = self.mw.reviewer.card
        self.editor.set_note(self.mw.reviewer.card.note(), focusTo=0)
        restoreGeom(self, "editcurrent")
        close_button = self.form.buttonBox.button(QDialogButtonBox.StandardButton.Close)
        assert close_button is not None
        close_button.setShortcut(QKeySequence("Ctrl+Return"))
        add_close_shortcut(self)
        # qt5.14+ doesn't handle numpad enter on Windows
        self.compat_add_shorcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
        qconnect(self.compat_add_shorcut.activated, close_button.click)
        gui_hooks.operation_did_execute.append(self.on_operation_did_execute)
        self.show()

    def on_operation_did_execute(
        self, changes: OpChanges, handler: object | None
    ) -> None:
        if changes.note_text and handler is not self.editor:
            # reload note
            note = self.editor.note
            try:
                assert note is not None
                note.load()
            except NotFoundError:
                # note's been deleted
                self.cleanup()
                self.close()
                return

            self.editor.set_note(note)

    def cleanup(self) -> None:
        gui_hooks.operation_did_execute.remove(self.on_operation_did_execute)
        self.editor.cleanup()
        saveGeom(self, "editcurrent")
        aqt.dialogs.markClosed("EditCurrent")

    def reopen(self, mw: aqt.AnkiQt) -> None:
        if card := self.mw.reviewer.card:
            self.editor.card = card
            self.editor.set_note(card.note())

    def closeEvent(self, evt: QCloseEvent | None) -> None:
        self.editor.call_after_note_saved(self.cleanup)

    def _saveAndClose(self) -> None:
        self.cleanup()
        self.mw.deferred_delete_and_garbage_collect(self)
        self.close()

    def closeWithCallback(self, onsuccess: Callable[[], None]) -> None:
        def callback() -> None:
            self._saveAndClose()
            onsuccess()

        self.editor.call_after_note_saved(callback)

    onReset = on_operation_did_execute
