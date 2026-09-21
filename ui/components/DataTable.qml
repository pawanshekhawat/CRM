import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    property var model: []
    property var columns: []
    property int rowHeight: 52
    property int headerHeight: 42
    property bool showPagination: true
    property int pageSize: 25
    property int currentPage: 1
    property int totalRecords: model ? model.length : 0
    property int totalPages: Math.max(1, Math.ceil(totalRecords / pageSize))

    property string emptyTitle: "No records found"
    property string emptyMessage: "No data matches the current criteria."
    property string emptyButtonText: ""

    property string activeSortRole: ""
    property string activeSortDirection: "desc"

    signal headerClicked(var columnDef, int index)
    signal rowClicked(var rowData, int index)
    signal rowDoubleClicked(var rowData, int index)
    signal rowAction(string action, var rowData, int index)
    signal statusChanged(var rowData, string newStatus, int index)
    signal emptyActionClicked()

    radius: Theme.radiusLG
    color: Theme.surface
    border.color: Theme.border
    border.width: 1
    clip: true

    // Sliced page data
    readonly property var pagedModel: {
        if (!model || model.length === 0) return [];
        if (!showPagination) return model;
        var start = (currentPage - 1) * pageSize;
        var end = Math.min(start + pageSize, model.length);
        return model.slice(start, end);
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Table Header
        Rectangle {
            Layout.fillWidth: true
            height: root.headerHeight
            color: Theme.surfaceElevated
            border.color: Theme.borderSubtle
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingMD
                anchors.rightMargin: Theme.spacingMD
                spacing: Theme.spacingSM

                Repeater {
                    model: root.columns

                    Rectangle {
                        id: headerCell
                        Layout.preferredWidth: modelData.width ? modelData.width : (modelData.fill ? 0 : 120)
                        Layout.fillWidth: modelData.fill ? true : false
                        Layout.fillHeight: true
                        color: (headerMouse.containsMouse && !modelData.isAction) ? Theme.surfaceHover : "transparent"
                        radius: Theme.radiusSM

                        Behavior on color { ColorAnimation { duration: Theme.animFast } }

                        readonly property bool isSorted: Boolean(root.activeSortRole !== "" && (root.activeSortRole === modelData.role || (modelData.sortRole ? root.activeSortRole === modelData.sortRole : false)))

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 4
                            anchors.rightMargin: 4
                            spacing: 4

                            Text {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignVCenter
                                text: modelData.title || ""
                                color: headerCell.isSorted ? Theme.primaryText :
                                       (headerMouse.containsMouse && !modelData.isAction ? Theme.textPrimary : Theme.textSecondary)
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                                font.weight: headerCell.isSorted ? Theme.weightBold : Theme.weightDemiBold
                                elide: Text.ElideRight
                                horizontalAlignment: modelData.alignRight ? Text.AlignRight : Text.AlignLeft
                            }

                            // Sort Icon Indicator
                            Icon {
                                visible: !modelData.isAction
                                name: headerCell.isSorted ? (root.activeSortDirection === "asc" ? "chevron-up" : "chevron-down") : "sort"
                                size: 11
                                color: headerCell.isSorted ? Theme.primary : (headerMouse.containsMouse ? Theme.textPrimary : Theme.border)
                                opacity: headerCell.isSorted ? 1.0 : (headerMouse.containsMouse ? 0.8 : 0.35)
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }

                        MouseArea {
                            id: headerMouse
                            anchors.fill: parent
                            hoverEnabled: !modelData.isAction
                            cursorShape: !modelData.isAction ? Qt.PointingHandCursor : Qt.ArrowCursor
                            enabled: !modelData.isAction
                            onClicked: {
                                root.headerClicked(modelData, index);
                            }
                        }
                    }
                }
            }
        }

        // Table Body / ListView
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: listView
                anchors.fill: parent
                model: root.pagedModel
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ScrollBar.vertical: ScrollBar {
                    active: true
                    policy: ScrollBar.AsNeeded
                }

                delegate: Rectangle {
                    id: rowItem
                    width: listView.width
                    height: root.rowHeight
                    color: rowMouse.containsMouse ? Theme.surfaceHover :
                           (index % 2 === 1 ? Qt.rgba(Theme.surfaceElevated.r, Theme.surfaceElevated.g, Theme.surfaceElevated.b, 0.4) : "transparent")

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }

                    // Row bottom separator line
                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: 1
                        color: Theme.borderSubtle
                    }

                    // Background MouseArea for row clicks and double-clicks
                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.rowClicked(modelData_row, index)
                        onDoubleClicked: root.rowDoubleClicked(modelData_row, index)
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingMD
                        anchors.rightMargin: Theme.spacingMD
                        spacing: Theme.spacingSM

                        Repeater {
                            model: root.columns

                            Item {
                                id: cellItem
                                readonly property var colDef: modelData
                                readonly property var rowData: modelData_row
                                Layout.preferredWidth: colDef.width ? colDef.width : (colDef.fill ? 0 : 120)
                                Layout.fillWidth: colDef.fill ? true : false
                                Layout.fillHeight: true

                                // 1. Avatar with Name & Subtitle cell (Student photo + Name + ID)
                                RowLayout {
                                    visible: colDef.isAvatarWithName === true
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    spacing: 10

                                    Avatar {
                                        name: String(modelData_row.name || "")
                                        photoUrl: String(modelData_row.photo_url || "")
                                        size: 32
                                        Layout.alignment: Qt.AlignVCenter
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 1
                                        Layout.alignment: Qt.AlignVCenter

                                        Text {
                                            text: String(modelData_row.name || "")
                                            color: Theme.textPrimary
                                            font.family: Theme.fontFamily
                                            font.pixelSize: Theme.fontBody
                                            font.weight: Theme.weightMedium
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }

                                        Text {
                                            text: String(modelData_row.id_no || "")
                                            color: Theme.textMuted
                                            font.family: Theme.fontMono
                                            font.pixelSize: 10
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }
                                    }
                                }

                                // 2. Standalone Avatar cell
                                Avatar {
                                    visible: colDef.isAvatar === true && !colDef.isAvatarWithName
                                    anchors.verticalCenter: parent.verticalCenter
                                    name: String(modelData_row[colDef.role] || "")
                                    photoUrl: String(modelData_row.photo_url || "")
                                    size: 32
                                }

                                // 3. Date with Subtitle cell (e.g. Last Fee Paid Date + 15 days ago)
                                ColumnLayout {
                                    visible: colDef.isDateWithSubtitle === true
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    spacing: 1

                                    RowLayout {
                                        spacing: 5
                                        Text {
                                            text: "🗓️"
                                            font.pixelSize: 11
                                        }
                                        Text {
                                            text: String(modelData_row[colDef.role] || "—")
                                            color: modelData_row[colDef.role] && modelData_row[colDef.role] !== "—" ? Theme.textPrimary : Theme.textMuted
                                            font.family: Theme.fontFamily
                                            font.pixelSize: Theme.fontBody
                                            font.weight: Theme.weightMedium
                                            elide: Text.ElideRight
                                        }
                                    }

                                    Text {
                                        text: String(modelData_row[colDef.subtitleRole || "days_ago_str"] || "")
                                        color: {
                                            var d = modelData_row.days_ago;
                                            if (d !== undefined && d >= 0) {
                                                if (d <= 15) return Theme.successText;
                                                if (d <= 45) return Theme.warningText;
                                                return Theme.dangerText;
                                            }
                                            return Theme.textMuted;
                                        }
                                        font.family: Theme.fontFamily
                                        font.pixelSize: 10
                                        font.weight: Theme.weightNormal
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                }

                                // 4. Standard Text cell
                                Text {
                                    visible: !colDef.isBadge && !colDef.isStatusDropdown && !colDef.isAction && !colDef.isAvatar && !colDef.isAvatarWithName && !colDef.isDateWithSubtitle
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    text: {
                                        var val = modelData_row[colDef.role];
                                        if (val === undefined || val === null) return "";
                                        if (colDef.isCurrency) return "₹" + Number(val).toLocaleString("en-IN");
                                        return String(val);
                                    }
                                    color: colDef.isPrimary ? Theme.textPrimary :
                                           (colDef.isMuted ? Theme.textMuted :
                                           (colDef.isHighlight ? Theme.primaryText : Theme.textSecondary))
                                    font.family: colDef.isCurrency ? Theme.fontMono : Theme.fontFamily
                                    font.pixelSize: Theme.fontBody
                                    font.weight: colDef.isPrimary || colDef.isHighlight ? Theme.weightMedium : Theme.weightNormal
                                    elide: Text.ElideRight
                                    horizontalAlignment: colDef.alignRight ? Text.AlignRight : Text.AlignLeft
                                }

                                // 5. Status Badge cell
                                StatusBadge {
                                    visible: colDef.isBadge === true && !colDef.isStatusDropdown
                                    anchors.verticalCenter: parent.verticalCenter
                                    status: String(modelData_row[colDef.role] || "Active")
                                }

                                // 6. Interactive Status Dropdown cell
                                StatusDropdown {
                                    visible: colDef.isStatusDropdown === true
                                    anchors.verticalCenter: parent.verticalCenter
                                    currentStatus: String(modelData_row[colDef.role] || "Active")
                                    z: 20
                                    onStatusSelected: newStatus => {
                                        root.statusChanged(modelData_row, newStatus, index);
                                    }
                                }

                                // 7. Action Buttons cell (Elevated z-index to handle clicks independently)
                                Row {
                                    visible: colDef.isAction === true
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.right: colDef.alignRight ? parent.right : undefined
                                    spacing: 4
                                    z: 10

                                    Repeater {
                                        model: colDef.actions || ["eye", "edit"]

                                        IconButton {
                                            iconName: modelData
                                            iconSize: 14
                                            buttonSize: 30
                                            tooltip: {
                                                switch (modelData) {
                                                    case "eye":
                                                    case "view": return "View Student Profile & Ledger";
                                                    case "fees": return "Record Fee Payment";
                                                    case "download": return "Generate Admission Slip";
                                                    case "trash": return "Delete Student Record";
                                                    case "whatsapp": return "Dispatch WhatsApp";
                                                    default: return "";
                                                }
                                            }
                                            hoverIconColor: modelData === "trash" ? Theme.danger : (modelData === "fees" ? Theme.accent : Theme.primary)
                                            onClicked: root.rowAction(modelData, modelData_row, index)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Expose row data cleanly
                    property var modelData_row: modelData
                }
            }

            // Empty State
            EmptyState {
                anchors.centerIn: parent
                visible: !root.model || root.model.length === 0
                iconName: "search"
                title: root.emptyTitle
                message: root.emptyMessage
                buttonText: root.emptyButtonText
                onActionClicked: root.emptyActionClicked()
            }
        }

        // Table Footer / Pagination
        Rectangle {
            visible: root.showPagination && root.totalRecords > 0
            Layout.fillWidth: true
            height: 46
            color: Theme.surfaceElevated
            border.color: Theme.borderSubtle
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingMD
                anchors.rightMargin: Theme.spacingMD
                spacing: Theme.spacingMD

                Text {
                    readonly property int startRec: root.totalRecords === 0 ? 0 : (root.currentPage - 1) * root.pageSize + 1
                    readonly property int endRec: Math.min(root.currentPage * root.pageSize, root.totalRecords)
                    text: `Showing ${startRec} - ${endRec} of ${root.totalRecords} records`
                    color: Theme.textMuted
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                }

                Item { Layout.fillWidth: true }

                RowLayout {
                    spacing: 6

                    IconButton {
                        iconName: "chevron-left"
                        iconSize: 14
                        buttonSize: 30
                        enabled: root.currentPage > 1
                        onClicked: if (root.currentPage > 1) root.currentPage--
                    }

                    Text {
                        text: `Page ${root.currentPage} of ${root.totalPages}`
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSmall
                        font.weight: Theme.weightMedium
                        Layout.alignment: Qt.AlignVCenter
                    }

                    IconButton {
                        iconName: "chevron-right"
                        iconSize: 14
                        buttonSize: 30
                        enabled: root.currentPage < root.totalPages
                        onClicked: if (root.currentPage < root.totalPages) root.currentPage++
                    }
                }
            }
        }
    }
}
