from PySide6.QtWidgets import QLayout


def clear_layout(layout: QLayout):
    if layout is None:
        return

    # Loop backwards or while count > 0
    while layout.count():
        # 1. Take the item out of the layout list
        item = layout.takeAt(0)

        # 2. If the item is a widget, delete it
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

        # 3. If the item is a nested layout, clear it recursively (optional but recommended)
        elif item.layout() is not None:
            clear_layout(item.layout())