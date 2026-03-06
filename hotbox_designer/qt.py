"""
Qt compatibility shim for hotbox_designer.
Supports PySide2 (Python 2.7 / 3.x) and PySide6 (Python 3.x).

Usage in other modules:
    from hotbox_designer.qt import QtCore, QtGui, QtWidgets, QtCompat
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import Qt
    PYSIDE_VERSION = 2


# ---------------------------------------------------------------------------
# QRegExp -> QRegularExpression
# PySide6 removed QtCore.QRegExp.  Provide a thin wrapper so existing code
# that uses the QRegExp API (indexIn / matchedLength) works on both versions.
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    import re as _re

    class QRegExp(object):
        """Minimal QRegExp compatibility wrapper for PySide6."""

        def __init__(self, pattern):
            self._pattern = pattern
            self._regex = _re.compile(pattern)
            self._last_match = None
            self._last_text = ''
            self._last_pos = 0

        def indexIn(self, text, offset=0):
            self._last_text = text
            m = self._regex.search(text, offset)
            if m is None:
                self._last_match = None
                return -1
            self._last_match = m
            return m.start()

        def matchedLength(self):
            if self._last_match is None:
                return -1
            return self._last_match.end() - self._last_match.start()

    QtCore.QRegExp = QRegExp


# ---------------------------------------------------------------------------
# QPalette.Background -> QPalette.Window  (removed in Qt6)
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    if not hasattr(QtGui.QPalette, 'Background'):
        QtGui.QPalette.Background = QtGui.QPalette.Window


# ---------------------------------------------------------------------------
# exec_() compatibility
# QDialog.exec_() was kept as an alias in PySide6, but patch it just in case.
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    if not hasattr(QtWidgets.QDialog, 'exec_'):
        QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec


# ---------------------------------------------------------------------------
# QDialog.Accepted / QDialog.Rejected  (moved to Qt namespace in PySide6)
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    if not hasattr(QtWidgets.QDialog, 'Accepted'):
        QtWidgets.QDialog.Accepted = QtWidgets.QDialog.DialogCode.Accepted
        QtWidgets.QDialog.Rejected = QtWidgets.QDialog.DialogCode.Rejected


# ---------------------------------------------------------------------------
# Qt namespace flags that moved inside sub-enums in PySide6
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    _Qt = QtCore.Qt
    # Window flags
    for _attr in ('WindowStaysOnTopHint', 'FramelessWindowHint', 'Tool',
                  'Window'):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.WindowType, _attr))
    # Widget attributes
    for _attr in ('WA_TranslucentBackground',):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.WidgetAttribute, _attr))
    # Key enums
    for _attr in ('Key_Escape',):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.Key, _attr))
    # Mouse buttons
    for _attr in ('LeftButton', 'RightButton'):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.MouseButton, _attr))
    # Focus reasons
    for _attr in ('MouseFocusReason',):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.FocusReason, _attr))
    # Pen / Brush styles
    for _attr in ('SolidLine', 'DashLine', 'DashDotLine', 'FDiagPattern',
                  'MiterJoin'):
        if not hasattr(_Qt, _attr):
            for _enum in ('PenStyle', 'BrushStyle', 'PenJoinStyle'):
                _enum_obj = getattr(_Qt, _enum, None)
                if _enum_obj and hasattr(_enum_obj, _attr):
                    setattr(_Qt, _attr, getattr(_enum_obj, _attr))
                    break
    # Alignment
    for _attr in ('AlignTop', 'AlignVCenter', 'AlignBottom',
                  'AlignLeft', 'AlignHCenter', 'AlignRight'):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.AlignmentFlag, _attr))
    # Cap styles
    for _attr in ('RoundCap',):
        if not hasattr(_Qt, _attr):
            setattr(_Qt, _attr, getattr(_Qt.PenCapStyle, _attr))
    # Render hints
    if not hasattr(QtGui.QPainter, 'Antialiasing'):
        QtGui.QPainter.Antialiasing = (
            QtGui.QPainter.RenderHint.Antialiasing)


# ---------------------------------------------------------------------------
# QAction moved from QtWidgets to QtGui in PySide6
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    if not hasattr(QtWidgets, 'QAction'):
        QtWidgets.QAction = QtGui.QAction


# ---------------------------------------------------------------------------
# QHeaderView resize modes (moved to QHeaderView.ResizeMode in PySide6)
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    _HV = QtWidgets.QHeaderView
    for _attr in ('ResizeToContents', 'Stretch', 'Fixed', 'Interactive',
                  'Custom'):
        if not hasattr(_HV, _attr) and hasattr(_HV.ResizeMode, _attr):
            setattr(_HV, _attr, getattr(_HV.ResizeMode, _attr))


# ---------------------------------------------------------------------------
# QAbstractItemView selection/scroll enums (moved to sub-enums in PySide6)
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    _AIV = QtWidgets.QAbstractItemView
    for _attr in ('SelectRows', 'SelectColumns', 'SelectItems'):
        if not hasattr(_AIV, _attr) and hasattr(_AIV.SelectionBehavior, _attr):
            setattr(_AIV, _attr, getattr(_AIV.SelectionBehavior, _attr))
    for _attr in ('SingleSelection', 'MultiSelection', 'ExtendedSelection',
                  'ContiguousSelection', 'NoSelection'):
        if not hasattr(_AIV, _attr) and hasattr(_AIV.SelectionMode, _attr):
            setattr(_AIV, _attr, getattr(_AIV.SelectionMode, _attr))


# ---------------------------------------------------------------------------
# QMessageBox buttons (moved to sub-enum in PySide6)
# ---------------------------------------------------------------------------
if PYSIDE_VERSION == 6:
    if not hasattr(QtWidgets.QMessageBox, 'Ok'):
        QtWidgets.QMessageBox.Ok = QtWidgets.QMessageBox.StandardButton.Ok


# ---------------------------------------------------------------------------
# QtCompat helper: wrap / unwrap native widget pointers (shiboken)
# ---------------------------------------------------------------------------
class QtCompat(object):
    """Thin shiboken compatibility layer."""

    @staticmethod
    def wrapInstance(ptr, base=None):
        if base is None:
            base = QtWidgets.QWidget
        if PYSIDE_VERSION == 6:
            import shiboken6
            return shiboken6.wrapInstance(int(ptr), base)
        else:
            import shiboken2
            # Python 2 needs long(), Python 3 uses int()
            try:
                ptr = long(ptr)
            except NameError:
                ptr = int(ptr)
            return shiboken2.wrapInstance(ptr, base)
