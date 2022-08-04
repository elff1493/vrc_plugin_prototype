import QtQuick 2.12
import QtQuick.Window 2.2
import QtQuick.Controls 2.12
import QtQuick.Controls.Styles 1.4

Switch {
    text: symbol_name
    background: Rectangle {
    color: red
    }
    onToggled: {
        self.on_changed()
    }
 }