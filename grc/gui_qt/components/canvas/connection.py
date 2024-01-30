from qtpy import QtGui, QtCore, QtWidgets

from ....core.Connection import Connection as CoreConnection
from . import colors
from ...Constants import (
    CONNECTOR_ARROW_BASE,
    CONNECTOR_ARROW_HEIGHT
)


class DummyConnection(QtWidgets.QGraphicsPathItem):
    """
    Dummy connection used for when the user drags a connection
    between two ports.
    """
    def __init__(self, parent, start_point, end_point):
        QtWidgets.QGraphicsItem.__init__(self)

        self.start_point = start_point
        self._line = QtGui.QPainterPath()
        self._arrowhead = QtGui.QPainterPath()
        self._path = QtGui.QPainterPath()
        self._current_port_rotations = self._current_coordinates = None
        self._arrow_rotation = 0.0  # TODO: rotation of the arrow in radians
        self.update(end_point)

    def update(self, end_point):
        """User moved the mouse, redraw with new end point"""
        self._line.clear()
        self._line.moveTo(self.start_point)
        c1 = self.start_point + QtCore.QPointF(200, 0)
        c2 = end_point - QtCore.QPointF(200, 0)
        self._line.cubicTo(c1, c2, end_point)

        self._arrowhead.clear()
        self._arrowhead.moveTo(end_point)
        self._arrowhead.lineTo(end_point + QtCore.QPointF(-CONNECTOR_ARROW_HEIGHT, - CONNECTOR_ARROW_BASE / 2))
        self._arrowhead.lineTo(end_point + QtCore.QPointF(-CONNECTOR_ARROW_HEIGHT, CONNECTOR_ARROW_BASE / 2))
        self._arrowhead.lineTo(end_point)

        self._path.clear()
        self._path.addPath(self._line)
        self._path.addPath(self._arrowhead)
        self.setPath(self._path)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(0x61, 0x61, 0x61))
        painter.setBrush(QtGui.QColor(0x61, 0x61, 0x61))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(self._line)
        painter.drawPath(self._arrowhead)


class Connection(CoreConnection):
    def __init__(self, parent, source, sink):
        super(Connection, self).__init__(parent, source, sink)


class GUIConnection(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent, source, sink):
        self.core = parent.core.connect(source.core, sink.core)
        self.core.gui = self
        super(GUIConnection, self).__init__()

        self.source = source
        self.sink = sink

        self._line = QtGui.QPainterPath()
        self._arrowhead = QtGui.QPainterPath()
        self._path = QtGui.QPainterPath()
        self.update()

        self._line_width_factor = 1.0
        self._color1 = self._color2 = None

        self._current_port_rotations = self._current_coordinates = None

        self._rel_points = None  # connection coordinates relative to sink/source
        self._arrow_rotation = 0.0  # rotation of the arrow in radians
        self._current_cr = None  # for what_is_selected() of curved line
        self._line_path = None
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    def update(self):
        """
        Source and sink moved in relation to each other, redraw with new end points
        """
        self._line.clear()
        self._line.moveTo(self.source.connection_point)
        c1 = self.source.connection_point + QtCore.QPointF(200, 0)
        c2 = self.sink.connection_point - QtCore.QPointF(200, 0)
        self._line.cubicTo(c1, c2, self.sink.connection_point)

        self._arrowhead.clear()
        self._arrowhead.moveTo(self.sink.connection_point)
        self._arrowhead.lineTo(self.sink.connection_point + QtCore.QPointF(-CONNECTOR_ARROW_HEIGHT, - CONNECTOR_ARROW_BASE / 2))
        self._arrowhead.lineTo(self.sink.connection_point + QtCore.QPointF(-CONNECTOR_ARROW_HEIGHT, CONNECTOR_ARROW_BASE / 2))
        self._arrowhead.lineTo(self.sink.connection_point)

        self._path.clear()
        self._path.addPath(self._line)
        self._path.addPath(self._arrowhead)
        self.setPath(self._path)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        color = QtGui.QColor(0x61, 0x61, 0x61)
        if self.isSelected():
            color = colors.HIGHLIGHT_COLOR
        elif not self.core.enabled:
            color = colors.CONNECTION_DISABLED_COLOR
        elif not self.core.is_valid():
            color = colors.CONNECTION_ERROR_COLOR

        pen = QtGui.QPen(color)

        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(self._line)
        painter.setBrush(color)
        painter.drawPath(self._arrowhead)

    def mouseDoubleClickEvent(self, e):
        self.parent.connections.remove(self)
        self.parent.removeItem(self)
