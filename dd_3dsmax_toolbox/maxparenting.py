"""This is a quite well working experiment of setting the **owner**
(not the **parent**) of the qt widget to be the 3dsMax main window.
Effectively the qt widget will behave like a natively spawned window,
with correct z-order behaviour concerning its sibling windows.
"""

import ctypes

from PySide import QtGui
from PySide import QtCore
import MaxPlus

GWL_HWNDPARENT = -8
SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW

class FocusFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        # TODO: fix focus filter not releasing on defocus
        MaxPlus.CUI.DisableAccelerators()
        return False

class MaxWidget(QtGui.QWidget):
    def __init__(self, title):
        super(MaxWidget, self).__init__(None)
        self.parent_hwnd = MaxPlus.Win32.GetMAXHWnd()
        self.hwnd = self.get_hwnd()
        self._parent_to_main_window()
        self.show()
        app = QtGui.QApplication.instance()
        self._focus_filter = FocusFilter()
        self.event_filter = app.installEventFilter(self._focus_filter)
        self.resize(310, 210)
        self.setStyleSheet("""
            QWidget {
                font-family: MS Shell Dlg 2;
            }
        
            QListView {
                outline: none;
                show-decoration-selected: 1; /* make the selection span the entire width of the view */
            }
            
            QListView::item {              
                margin-left: 0px;
                border: 1px solid rgba(0, 0, 0, 0);
            }
            
            QListView::item:alternate {
                background: #EEEEEE;
            }
            
            QListView::item:selected {
                color: white;
                border: 1px solid rgba(255, 165, 0, 200);
            }
            
            QListView::item:selected:!active {                
                background: rgba(255, 165, 0, 32);                
            }
            
            QListView::item:selected:active {
                background: rgba(255, 165, 0, 32);                
            }
            
            QListView::item:hover {
                background: rgba(255, 165, 0, 0);                
            }
            
            QLineEdit
            {    
                background: rgba(25, 25, 25, 255);
                padding: 0px;
                margin-left: 1px;
                margin-right: -2px;
                border-style: none;
                font-size: 12px;
                selection-color: black;
                selection-background-color: rgba(255, 165, 0, 200);
            }
            """
        )
        #print(self.font().family())

    def get_hwnd(self):
        """Get the HWND window handle from this QtWidget."""
        ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
        wdgt_ptr = ctypes.pythonapi.PyCObject_AsVoidPtr(self.winId())
        return wdgt_ptr

    def _parent_to_main_window(self):
        """ Parent the widget to the 3dsMax main window.
        Technically this is NOT setting the **parent** of the window,
        but the **owner**.
        There is a huge difference, that is hardly documented in the
        win32 API.
        https://msdn.microsoft.com/en-us/library/windows/desktop/ms644898(v=vs.85).aspx  # noqa
        Setting the parent would make this a child or mdi-
        child window. Setting the owner, makes this a top-level,
        overlapped window that is controlled by the main window, but
        not confined to its client area.
        http://stackoverflow.com/questions/133122/
        """
        SetWindowLongPtr(self.hwnd, GWL_HWNDPARENT, self.parent_hwnd)

    def closeEvent(self, event):
        app = QtGui.QApplication.instance()
        app.removeEventFilter(self.event_filter)
        event.accept()