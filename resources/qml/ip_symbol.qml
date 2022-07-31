
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12


Row {
        id: row
        Text {
            text: symbol_name
            padding:3
            anchors.verticalCenter: parent.verticalCenter
            }

        Text {
            text: " - "
            padding:3
            anchors.verticalCenter: parent.verticalCenter
            }

        Tumbler {
            id: ip0
            model: 255
            implicitHeight: 15*visibleItemCount
            implicitWidth: 20
            visibleItemCount: 3
            onCurrentIndexChanged: {
            self.on_changed()
            }
            delegate: delegateComponent
            Connections {

                            onDataChanged: self.on_changed()
                        }
        }
        Text {
            text: "."
            anchors.verticalCenter: parent.verticalCenter
            }
        Tumbler {
            id: ip1
            model: 255
            implicitHeight: 15*visibleItemCount
            implicitWidth: 20
            visibleItemCount: 3
            onCurrentIndexChanged: {
            self.on_changed()
            }
            delegate: delegateComponent
        }
        Text {
            text: "."
            anchors.verticalCenter: parent.verticalCenter
            }
        Tumbler {
            id: ip2
            model: 255
            implicitHeight: 15*visibleItemCount
            implicitWidth: 20
            visibleItemCount: 3
            onCurrentIndexChanged: {
            self.on_changed()
            }
            delegate: delegateComponent
        }
        Text {
            text: "."
            anchors.verticalCenter: parent.verticalCenter
            }
        Tumbler {
            id: ip3
            model: 255
            implicitHeight: 15*visibleItemCount
            implicitWidth: 20
            visibleItemCount: 3
            onCurrentIndexChanged: {
            self.on_changed()
            }
            delegate: delegateComponent
        }


}