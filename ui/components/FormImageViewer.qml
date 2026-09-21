import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../theme"

Item {
    id: root

    property string imageUrl: ""
    property string rawFilePath: ""
    property string studentId: ""
    property string studentName: ""
    property string studentIdNo: ""
    property bool isFullscreenLightbox: false

    // Zoom & transform state
    property real zoomFactor: 1.0
    property int rotationAngle: 0
    property real minZoom: 0.25
    property real maxZoom: 4.0

    implicitWidth: 800
    implicitHeight: 600

    function resetTransform() {
        zoomFactor = 1.0;
        rotationAngle = 0;
        flick.contentX = Math.max(0, (flick.contentWidth - flick.width) / 2);
        flick.contentY = 0;
    }

    function zoomIn() {
        zoomFactor = Math.min(maxZoom, zoomFactor + 0.25);
    }

    function zoomOut() {
        zoomFactor = Math.max(minZoom, zoomFactor - 0.25);
    }

    function rotateClockwise() {
        rotationAngle = (rotationAngle + 90) % 360;
    }

    function fitToWidth() {
        if (img.implicitWidth > 0 && flick.width > 0) {
            var targetW = flick.width - 40;
            zoomFactor = Math.max(minZoom, Math.min(maxZoom, targetW / img.implicitWidth));
            flick.contentX = 0;
            flick.contentY = 0;
        }
    }

    function openInSystemViewer() {
        var path = root.rawFilePath;
        if (!path && root.imageUrl) {
            path = root.imageUrl.replace("file:///", "").replace("file://", "");
        }
        if (path && typeof reportsBridge !== "undefined") {
            reportsBridge.openDocument(path);
            if (typeof crmBridge !== "undefined") {
                crmBridge.showToast("Opening scanned form in system image viewer...", "info", "External Viewer");
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingMD

        // Top Toolbar
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 52
            radius: Theme.radiusMD
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingMD
                anchors.rightMargin: Theme.spacingMD
                spacing: Theme.spacingSM

                Icon {
                    name: "document"
                    size: 18
                    color: Theme.accent
                }

                Text {
                    text: root.imageUrl ? "Scanned Physical Admission Form" : "Physical Form Archive"
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontBody
                    font.weight: Theme.weightBold
                }

                Rectangle {
                    visible: root.imageUrl !== ""
                    height: 22
                    radius: Theme.radiusSM
                    color: Theme.successSoft
                    border.color: Theme.success
                    border.width: 1
                    implicitWidth: docBadgeText.implicitWidth + 12

                    Text {
                        id: docBadgeText
                        anchors.centerIn: parent
                        text: "Verified Document"
                        color: Theme.successText
                        font.family: Theme.fontFamily
                        font.pixelSize: 11
                        font.weight: Theme.weightBold
                    }
                }

                Item { Layout.fillWidth: true }

                // Zoom Controls Group
                RowLayout {
                    visible: root.imageUrl !== ""
                    spacing: 4

                    SecondaryButton {
                        iconName: "zoom-out"
                        customHeight: 32
                        onClicked: root.zoomOut()
                    }

                    Rectangle {
                        height: 32
                        implicitWidth: 60
                        radius: Theme.radiusSM
                        color: Theme.surfaceElevated
                        border.color: Theme.borderSubtle
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: Math.round(root.zoomFactor * 100) + "%"
                            color: Theme.textPrimary
                            font.family: Theme.fontMono
                            font.pixelSize: Theme.fontSmall
                            font.weight: Theme.weightBold
                        }
                    }

                    SecondaryButton {
                        iconName: "zoom-in"
                        customHeight: 32
                        onClicked: root.zoomIn()
                    }
                }

                SecondaryButton {
                    visible: root.imageUrl !== ""
                    text: "Fit Width"
                    iconName: "fit"
                    customHeight: 32
                    onClicked: root.fitToWidth()
                }

                SecondaryButton {
                    visible: root.imageUrl !== ""
                    text: "Rotate"
                    iconName: "rotate"
                    customHeight: 32
                    onClicked: root.rotateClockwise()
                }

                SecondaryButton {
                    visible: root.imageUrl !== ""
                    text: "Reset"
                    iconName: "refresh"
                    customHeight: 32
                    onClicked: root.resetTransform()
                }

                SecondaryButton {
                    visible: root.imageUrl !== ""
                    text: "System Viewer"
                    iconName: "eye"
                    customHeight: 32
                    onClicked: root.openInSystemViewer()
                }

                PrimaryButton {
                    visible: root.imageUrl !== ""
                    text: "Fullscreen"
                    iconName: "fullscreen"
                    customHeight: 32
                    onClicked: root.isFullscreenLightbox = true
                }

                SecondaryButton {
                    text: root.imageUrl ? "Replace Scan" : "Upload Scanned Form"
                    iconName: "download"
                    customHeight: 32
                    onClicked: filePicker.open()
                }
            }
        }

        // Main Viewer Frame
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Theme.radiusLG
            color: "#070A10"
            border.color: Theme.border
            border.width: 1
            clip: true

            // When image is loaded
            Flickable {
                id: flick
                anchors.fill: parent
                anchors.margins: 8
                visible: root.imageUrl !== ""
                contentWidth: Math.max(width, imgContainer.width * root.zoomFactor)
                contentHeight: Math.max(height, imgContainer.height * root.zoomFactor)
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

                Item {
                    id: imgContainer
                    width: Math.max(flick.width, img.implicitWidth)
                    height: Math.max(flick.height, img.implicitHeight)

                    Image {
                        id: img
                        anchors.centerIn: parent
                        source: root.imageUrl
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        antialiasing: true
                        mipmap: true
                        asynchronous: true
                        scale: root.zoomFactor
                        rotation: root.rotationAngle

                        Behavior on scale {
                            NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
                        }
                        Behavior on rotation {
                            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                        }
                    }
                }

                // Mouse Wheel Zoom
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.NoButton
                    onWheel: wheel => {
                        if (wheel.angleDelta.y > 0) {
                            root.zoomIn();
                        } else {
                            root.zoomOut();
                        }
                        wheel.accepted = true;
                    }
                }
            }

            // Empty State when no form is available
            ColumnLayout {
                anchors.centerIn: parent
                visible: root.imageUrl === ""
                spacing: Theme.spacingMD
                width: Math.min(480, parent.width - 40)

                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 72
                    height: 72
                    radius: 36
                    color: Theme.surfaceElevated
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Icon {
                        anchors.centerIn: parent
                        name: "document"
                        size: 36
                        color: Theme.textMuted
                    }
                }

                Text {
                    text: "No Scanned Admission Form Attached"
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontTitle
                    font.weight: Theme.weightBold
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: `Upload a high-resolution scanned copy or mobile photo of the physical admission form for student "${root.studentName || 'Student'}" (${root.studentIdNo || ''}).`
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontBody
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                PrimaryButton {
                    text: "Upload Scanned Admission Form"
                    iconName: "download"
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: Theme.spacingSM
                    onClicked: filePicker.open()
                }
            }
        }
    }

    // File Picker for Uploading/Replacing Scanned Form
    FileDialog {
        id: filePicker
        title: "Select Scanned Admission Form Image"
        nameFilters: ["Image Files (*.jpg *.jpeg *.png *.webp *.bmp)"]
        onAccepted: {
            var selected = filePicker.selectedFile.toString();
            if (root.studentId && typeof studentsBridge !== "undefined") {
                var ok = studentsBridge.updateAdmissionForm(root.studentId, selected);
                if (ok) {
                    if (typeof crmBridge !== "undefined") {
                        crmBridge.showToast("Admission form updated successfully.", "success", "Form Saved");
                    }
                    if (typeof studentDetailsPage !== "undefined") {
                        studentDetailsPage.loadStudent(root.studentId);
                    }
                } else {
                    if (typeof crmBridge !== "undefined") {
                        crmBridge.showToast("Could not attach admission form.", "error", "Upload Failed");
                    }
                }
            }
        }
    }

    // Fullscreen Lightbox Modal
    Rectangle {
        id: lightboxModal
        anchors.fill: parent
        z: 9999
        visible: root.isFullscreenLightbox
        color: "#06080CEE"

        Shortcut {
            sequence: "Escape"
            enabled: root.isFullscreenLightbox
            onActivated: root.isFullscreenLightbox = false
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Lightbox Top Header
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 48
                radius: Theme.radiusMD
                color: "#161B26"
                border.color: Theme.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingMD
                    anchors.rightMargin: Theme.spacingMD
                    spacing: Theme.spacingSM

                    Icon { name: "document"; size: 20; color: Theme.accent }

                    Text {
                        text: `📄 Admission Form — ${root.studentName} (${root.studentIdNo})`
                        color: "#F8FAFC"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontTitle
                        font.weight: Theme.weightBold
                    }

                    Item { Layout.fillWidth: true }

                    RowLayout {
                        spacing: 4

                        SecondaryButton {
                            iconName: "zoom-out"
                            customHeight: 32
                            onClicked: root.zoomOut()
                        }

                        Rectangle {
                            height: 32
                            implicitWidth: 60
                            radius: Theme.radiusSM
                            color: Theme.surfaceElevated
                            border.color: Theme.borderSubtle
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: Math.round(root.zoomFactor * 100) + "%"
                                color: Theme.textPrimary
                                font.family: Theme.fontMono
                                font.pixelSize: Theme.fontSmall
                                font.weight: Theme.weightBold
                            }
                        }

                        SecondaryButton {
                            iconName: "zoom-in"
                            customHeight: 32
                            onClicked: root.zoomIn()
                        }
                    }

                    SecondaryButton {
                        text: "Fit Width"
                        iconName: "fit"
                        customHeight: 32
                        onClicked: {
                            if (lightboxImg.implicitWidth > 0 && lightboxFlick.width > 0) {
                                var targetW = lightboxFlick.width - 40;
                                root.zoomFactor = Math.max(root.minZoom, Math.min(root.maxZoom, targetW / lightboxImg.implicitWidth));
                            }
                        }
                    }

                    SecondaryButton {
                        text: "Rotate"
                        iconName: "rotate"
                        customHeight: 32
                        onClicked: root.rotateClockwise()
                    }

                    SecondaryButton {
                        text: "System Viewer"
                        iconName: "eye"
                        customHeight: 32
                        onClicked: root.openInSystemViewer()
                    }

                    SecondaryButton {
                        text: "Close (Esc)"
                        iconName: "close"
                        customHeight: 32
                        onClicked: root.isFullscreenLightbox = false
                    }
                }
            }

            // Lightbox Flickable Area
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: "#04060A"
                border.color: Theme.border
                border.width: 1
                clip: true

                Flickable {
                    id: lightboxFlick
                    anchors.fill: parent
                    anchors.margins: 12
                    contentWidth: Math.max(width, lightboxContainer.width * root.zoomFactor)
                    contentHeight: Math.max(height, lightboxContainer.height * root.zoomFactor)
                    boundsBehavior: Flickable.StopAtBounds

                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

                    Item {
                        id: lightboxContainer
                        width: Math.max(lightboxFlick.width, lightboxImg.implicitWidth)
                        height: Math.max(lightboxFlick.height, lightboxImg.implicitHeight)

                        Image {
                            id: lightboxImg
                            anchors.centerIn: parent
                            source: root.imageUrl
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                            antialiasing: true
                            mipmap: true
                            asynchronous: true
                            scale: root.zoomFactor
                            rotation: root.rotationAngle

                            Behavior on scale {
                                NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
                            }
                            Behavior on rotation {
                                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.NoButton
                        onWheel: wheel => {
                            if (wheel.angleDelta.y > 0) {
                                root.zoomIn();
                            } else {
                                root.zoomOut();
                            }
                            wheel.accepted = true;
                        }
                    }
                }
            }
        }
    }
}
