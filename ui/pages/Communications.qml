import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var templatesList: []
    property var recipientsList: []
    property var filteredRecipients: []
    property string recipientSearchQuery: ""
    property var coursesList: []
    property string selectedTemplateId: ""
    property string currentTemplateText: "{Dear|Hello|Respected} {name}, this is a gentle reminder from CADDESK Centre regarding your {course} course. Your outstanding fee balance is ₹{balance_due}. Your last payment was made on {last_paid_date} ({days_ago} days ago). Kindly settle the pending installment at the accounts desk. Thank you!"
    property string currentTemplateTitle: ""
    property string selectedAudience: "Pending Fees"
    property string selectedCourseFilter: "All"

    // Active Preview Student State
    property var previewStudent: ({
        "id": "1",
        "name": "Shivkant Batu",
        "mobile_no": "9828965484",
        "course_name": "AutoCAD",
        "balance_due": 10000,
        "last_paid_date_str": "01 Sep 2026",
        "days_ago": 15,
        "days_ago_str": "15 days ago"
    })

    property string livePreviewText: ""
    property string editMode: "template" // "template" or "direct"
    property string customDirectMessage: ""
    readonly property string finalMessageToSend: (editMode === "direct" && customDirectMessage.trim() !== "") ? customDirectMessage : livePreviewText

    function refresh() {
        if (typeof messagingBridge !== "undefined") {
            templatesList = messagingBridge.getTemplates();
            if (templatesList.length > 0 && !selectedTemplateId) {
                selectTemplate(templatesList[0]);
            } else {
                updatePreview();
            }
            refreshRecipients();
        }
        if (typeof coursesBridge !== "undefined") {
            coursesList = ["All"].concat(coursesBridge.getCourseNames());
        }
    }

    function selectTemplate(tmpl) {
        selectedTemplateId = tmpl.id;
        currentTemplateTitle = tmpl.title;
        currentTemplateText = tmpl.content;
        composerInput.text = tmpl.content;
        if (root.editMode === "direct") {
            root.editMode = "template";
        }
        updatePreview();
    }

    function updatePreview() {
        if (typeof messagingBridge !== "undefined") {
            var sId = root.previewStudent ? root.previewStudent.id : 0;
            livePreviewText = messagingBridge.previewMessage(currentTemplateText, sId, true);
        }
    }

    function refreshRecipients() {
        if (typeof messagingBridge !== "undefined") {
            recipientsList = messagingBridge.getRecipients(selectedAudience, selectedCourseFilter, "All");
            applyRecipientFilter();
        }
    }

    function applyRecipientFilter() {
        var res = recipientsList;
        if (recipientSearchQuery.trim() !== "") {
            var q = recipientSearchQuery.toLowerCase();
            res = res.filter(r =>
                (r.name && r.name.toLowerCase().includes(q)) ||
                (r.mobile_no && r.mobile_no.includes(q)) ||
                (r.course_name && r.course_name.toLowerCase().includes(q))
            );
        }
        filteredRecipients = res;
        if (filteredRecipients.length > 0 && (!previewStudent || !previewStudent.name)) {
            previewStudent = filteredRecipients[0];
            updatePreview();
        }
    }

    function selectStudentForMessaging(studentIdOrObj) {
        if (!studentIdOrObj) return;
        refresh();

        var sId = (typeof studentIdOrObj === "object") ? String(studentIdOrObj.id) : String(studentIdOrObj);
        var found = null;
        if (recipientsList && recipientsList.length > 0) {
            found = recipientsList.find(r => String(r.id) === sId);
        }

        if (found) {
            previewStudent = found;
        } else if (typeof studentIdOrObj === "object") {
            previewStudent = studentIdOrObj;
        } else if (typeof studentsBridge !== "undefined") {
            var st = studentsBridge.getStudentById(sId);
            if (st && st.id) {
                previewStudent = {
                    "id": String(st.id),
                    "id_no": st.id_no || "",
                    "name": st.name || "",
                    "mobile_no": st.mobile_no || "",
                    "course_name": st.course_name || "",
                    "balance_due": st.balance_due || 0,
                    "fee_status": st.fee_status || "Pending",
                    "fee_status_display": st.fee_status || "Pending",
                    "last_paid_date_str": st.last_payment_date_str || "—",
                    "days_ago": st.days_since_last_payment !== undefined ? st.days_since_last_payment : -1,
                    "days_ago_str": st.days_since_last_payment_str || ""
                };
            }
        }

        root.editMode = "template";
        if (typeof composerInput !== "undefined" && composerInput) {
            composerInput.text = root.currentTemplateText;
        }
        updatePreview();
    }

    function insertTag(tag) {
        composerInput.text = composerInput.text + " " + tag;
        root.currentTemplateText = composerInput.text;
        root.updatePreview();
    }

    function dispatchSingleMessage() {
        if (!root.previewStudent || !root.previewStudent.id) {
            crmBridge.showToast("Please select a student recipient first.", "warning", "No Student Selected");
            return;
        }
        var msg = root.finalMessageToSend;
        if (!msg.trim()) {
            crmBridge.showToast("Message content is empty.", "warning", "Empty Message");
            return;
        }
        var ok = messagingBridge.sendDirectWhatsApp(root.previewStudent.id, msg);
        if (ok) {
            crmBridge.showToast(`WhatsApp launched for ${root.previewStudent.name}`, "success", "Message Dispatched");
        }
    }

    function dispatchBatchQueue() {
        if (root.recipientsList.length === 0) {
            crmBridge.showToast("No recipients found in the target queue.", "warning", "Empty Queue");
            return;
        }
        if (root.previewStudent && root.previewStudent.id) {
            var msg = root.finalMessageToSend;
            var ok = messagingBridge.sendDirectWhatsApp(root.previewStudent.id, msg);
            if (ok) {
                crmBridge.showToast(`Dispatched message to ${root.previewStudent.name}.`, "success", "WhatsApp Launched");
            }
        }
    }

    Component.onCompleted: refresh()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Header
        PageHeader {
            title: "WhatsApp Message Automation"
            subtitle: "Compose customized messages, configure Spintax variations, and dispatch to candidate queues"
            countText: `${root.recipientsList.length} recipients in queue`

            PrimaryButton {
                text: "New Message Template"
                iconName: "plus"
                onClicked: templateEditorDrawer.openDrawer(null)
            }
        }

        // 3-Column Studio Layout
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingMD

            // 1. Left Panel: Message Templates
            Rectangle {
                Layout.preferredWidth: 220
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMD
                    spacing: Theme.spacingSM

                    Text {
                        text: "Message Templates"
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBody
                        font.weight: Theme.weightBold
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: root.templatesList
                        spacing: 6

                        delegate: Rectangle {
                            id: tmplItem
                            readonly property bool isSelected: root.selectedTemplateId === modelData.id
                            width: ListView.view ? ListView.view.width : 200
                            height: 54
                            radius: Theme.radiusMD
                            color: isSelected ? Theme.primarySoft :
                                   (tmplMouse.containsMouse ? Theme.surfaceHover : Theme.surfaceElevated)
                            border.color: isSelected ? Theme.primary : Theme.borderSubtle
                            border.width: 1

                            Behavior on color { ColorAnimation { duration: Theme.animFast } }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Theme.spacingSM
                                spacing: 2

                                Text {
                                    text: modelData.title
                                    color: tmplItem.isSelected ? Theme.primaryText : Theme.textPrimary
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSmall
                                    font.weight: Theme.weightMedium
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: modelData.category
                                        color: Theme.textMuted
                                        font.family: Theme.fontFamily
                                        font.pixelSize: 10
                                    }
                                }
                            }

                            MouseArea {
                                id: tmplMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.selectTemplate(modelData)
                            }
                        }
                    }
                }
            }

            // 2. Center Panel: Tags, Editable Message Studio & Mobile Phone WhatsApp Mockup
            Rectangle {
                id: centerPanel
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ScrollView {
                    anchors.fill: parent
                    clip: true
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded

                    ColumnLayout {
                        width: centerPanel.width - 32
                        anchors.margins: Theme.spacingMD
                        spacing: Theme.spacingMD

                        // Top Controls Header: Mode Switcher & Template Actions
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSM

                            // Mode Selector (Template vs Direct Edit)
                            Rectangle {
                                height: 32
                                radius: Theme.radiusMD
                                color: Theme.surfaceElevated
                                border.color: Theme.borderSubtle
                                border.width: 1
                                implicitWidth: modeRow.implicitWidth + 8

                                RowLayout {
                                    id: modeRow
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Rectangle {
                                        height: 24
                                        radius: Theme.radiusSM
                                        color: root.editMode === "template" ? Theme.primarySoft : "transparent"
                                        border.color: root.editMode === "template" ? Theme.primary : "transparent"
                                        border.width: 1
                                        implicitWidth: tmplModeTxt.implicitWidth + 12

                                        Text {
                                            id: tmplModeTxt
                                            anchors.centerIn: parent
                                            text: "📝 Template Mode"
                                            color: root.editMode === "template" ? Theme.primaryText : Theme.textSecondary
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 11
                                            font.weight: root.editMode === "template" ? Theme.weightBold : Theme.weightMedium
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                root.editMode = "template";
                                                composerInput.text = root.currentTemplateText;
                                                root.updatePreview();
                                            }
                                        }
                                    }

                                    Rectangle {
                                        height: 24
                                        radius: Theme.radiusSM
                                        color: root.editMode === "direct" ? Theme.accentSoft : "transparent"
                                        border.color: root.editMode === "direct" ? Theme.accent : "transparent"
                                        border.width: 1
                                        implicitWidth: directModeTxt.implicitWidth + 12

                                        Text {
                                            id: directModeTxt
                                            anchors.centerIn: parent
                                            text: "✏️ Direct Edit Message"
                                            color: root.editMode === "direct" ? Theme.accentHover : Theme.textSecondary
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 11
                                            font.weight: root.editMode === "direct" ? Theme.weightBold : Theme.weightMedium
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                root.editMode = "direct";
                                                if (!root.customDirectMessage) {
                                                    root.customDirectMessage = root.livePreviewText;
                                                }
                                                composerInput.text = root.customDirectMessage;
                                            }
                                        }
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }

                            SecondaryButton {
                                text: "Edit Template Def"
                                iconName: "edit"
                                customHeight: 30
                                onClicked: {
                                    var currentTmpl = root.templatesList.find(t => t.id === root.selectedTemplateId);
                                    templateEditorDrawer.openDrawer(currentTmpl || null);
                                }
                            }

                            SecondaryButton {
                                text: "Re-roll Spintax"
                                iconName: "refresh"
                                customHeight: 30
                                onClicked: {
                                    root.updatePreview();
                                    if (root.editMode === "direct") {
                                        root.customDirectMessage = root.livePreviewText;
                                        composerInput.text = root.customDirectMessage;
                                    }
                                }
                            }
                        }

                        // Top Merge Tags Bar (Screenshot Style)
                        RowLayout {
                            visible: root.editMode === "template"
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "💡 Insert:"
                                color: Theme.accent
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                                font.weight: Theme.weightBold
                            }

                            Flow {
                                Layout.fillWidth: true
                                spacing: 6

                                Repeater {
                                    model: [
                                        "{name}",
                                        "{course}",
                                        "{balance_due}",
                                        "{last_paid_date}",
                                        "{days_ago}",
                                        "{Dear|Hello}"
                                    ]

                                    Rectangle {
                                        height: 26
                                        radius: Theme.radiusSM
                                        color: Theme.surfaceElevated
                                        border.color: tagMouse.containsMouse ? Theme.primary : Theme.border
                                        border.width: 1
                                        implicitWidth: tagText.implicitWidth + 14

                                        Text {
                                            id: tagText
                                            anchors.centerIn: parent
                                            text: modelData
                                            color: tagMouse.containsMouse ? Theme.primaryText : Theme.textSecondary
                                            font.family: Theme.fontMono
                                            font.pixelSize: 11
                                            font.weight: Theme.weightBold
                                        }

                                        MouseArea {
                                            id: tagMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.insertTag(modelData)
                                        }
                                    }
                                }
                            }
                        }

                        // Message Editor Textarea
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 90
                            radius: Theme.radiusMD
                            color: Theme.surfaceElevated
                            border.color: root.editMode === "direct" ? Theme.accent : Theme.border
                            border.width: 1

                            ScrollView {
                                anchors.fill: parent
                                anchors.margins: 8
                                clip: true

                                TextArea {
                                    id: composerInput
                                    text: root.editMode === "direct" ? root.customDirectMessage : root.currentTemplateText
                                    placeholderText: root.editMode === "direct" ? "Type customized direct message for this student..." : "Enter WhatsApp message template with {tags} and {spintax|variations}..."
                                    color: Theme.textPrimary
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontBody
                                    wrapMode: Text.WordWrap
                                    background: null
                                    onTextChanged: {
                                        if (root.editMode === "direct") {
                                            root.customDirectMessage = text;
                                        } else {
                                            root.currentTemplateText = text;
                                            root.updatePreview();
                                        }
                                    }
                                }
                            }
                        }

                        // Mobile Phone Screen Frame Container (Centered Mobile Width: 380px)
                        Rectangle {
                            id: phoneFrame
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 380
                            width: 380
                            implicitWidth: 380
                            implicitHeight: 480
                            radius: 32
                            color: "#0B141A"
                            border.color: "#2C3E50"
                            border.width: 4
                            clip: true

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 0

                                // 1. Smartphone Top Status Bar & Camera Notch
                                Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 28
                                    color: "#182229"

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 16
                                        anchors.rightMargin: 16

                                        Text {
                                            text: Qt.formatTime(new Date(), "h:mm")
                                            color: "#E9EDEF"
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 11
                                            font.weight: Theme.weightBold
                                        }

                                        // Camera Pill Notch
                                        Rectangle {
                                            Layout.alignment: Qt.AlignHCenter
                                            width: 70
                                            height: 14
                                            radius: 7
                                            color: "#0B141A"
                                        }

                                        RowLayout {
                                            spacing: 4
                                            Text { text: "📶"; font.pixelSize: 10 }
                                            Text { text: "🔋 98%"; color: "#E9EDEF"; font.pixelSize: 10 }
                                        }
                                    }
                                }

                                // 2. WhatsApp Mobile App Header
                                Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 52
                                    color: "#182229"
                                    border.color: "#222D34"
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        spacing: 8

                                        Text {
                                            text: "←"
                                            color: "#E9EDEF"
                                            font.pixelSize: 16
                                            font.weight: Theme.weightBold
                                        }

                                        // Contact Initials Avatar
                                        Rectangle {
                                            width: 34
                                            height: 34
                                            radius: 17
                                            color: "#00A884"

                                            Text {
                                                anchors.centerIn: parent
                                                text: {
                                                    var n = root.previewStudent ? root.previewStudent.name : "Student";
                                                    var parts = n.trim().split(" ");
                                                    return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : n.slice(0, 2).toUpperCase();
                                                }
                                                color: "#FFFFFF"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: 12
                                                font.weight: Theme.weightBold
                                            }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 0

                                            Text {
                                                text: root.previewStudent ? root.previewStudent.name : "Shivkant Batu"
                                                color: "#E9EDEF"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: 13
                                                font.weight: Theme.weightBold
                                                elide: Text.ElideRight
                                                Layout.fillWidth: true
                                            }

                                            Text {
                                                text: `+91 ${root.previewStudent ? root.previewStudent.mobile_no : '9828965484'}`
                                                color: "#8696A0"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: 10
                                                elide: Text.ElideRight
                                            }
                                        }

                                        RowLayout {
                                            spacing: 12
                                            Text { text: "📹"; font.pixelSize: 14 }
                                            Text { text: "📞"; font.pixelSize: 14 }
                                            Text { text: "⋮"; color: "#8696A0"; font.pixelSize: 16; font.weight: Theme.weightBold }
                                        }
                                    }
                                }

                                // 3. WhatsApp Mobile Chat Canvas & Bubble Area
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#0B141A"

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 10

                                        // Centered TODAY Pill
                                        Rectangle {
                                            Layout.alignment: Qt.AlignHCenter
                                            height: 20
                                            radius: 6
                                            color: "#182229"
                                            border.color: "#222D34"
                                            border.width: 1
                                            implicitWidth: todayText.implicitWidth + 14

                                            Text {
                                                id: todayText
                                                anchors.centerIn: parent
                                                text: "TODAY"
                                                color: "#8696A0"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: 9
                                                font.weight: Theme.weightBold
                                            }
                                        }

                                        // Outgoing Emerald WhatsApp Bubble (Realistic Phone Width)
                                        Rectangle {
                                            Layout.alignment: Qt.AlignRight
                                            Layout.maximumWidth: parent.width * 0.90
                                            implicitWidth: Math.min(parent.width * 0.90, msgText.implicitWidth + 24)
                                            implicitHeight: msgCol.implicitHeight + 16
                                            radius: 10
                                            color: "#005C4B"

                                            ColumnLayout {
                                                id: msgCol
                                                anchors.fill: parent
                                                anchors.margins: 8
                                                spacing: 4

                                                Text {
                                                    id: msgText
                                                    text: root.finalMessageToSend
                                                    color: "#E9EDEF"
                                                    font.family: Theme.fontFamily
                                                    font.pixelSize: 12
                                                    wrapMode: Text.WordWrap
                                                    lineHeight: 1.2
                                                    Layout.fillWidth: true
                                                }

                                                RowLayout {
                                                    Layout.alignment: Qt.AlignRight
                                                    spacing: 3

                                                    Text {
                                                        text: Qt.formatTime(new Date(), "h:mm AP")
                                                        color: "#8696A0"
                                                        font.family: Theme.fontFamily
                                                        font.pixelSize: 9
                                                    }

                                                    Text {
                                                        text: "✓✓"
                                                        color: "#53BDEB"
                                                        font.pixelSize: 10
                                                        font.weight: Theme.weightBold
                                                    }
                                                }
                                            }
                                        }

                                        Item { Layout.fillHeight: true }
                                    }
                                }

                                // 4. WhatsApp Mobile Chat Input Footer
                                Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 48
                                    color: "#182229"
                                    border.color: "#222D34"
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        spacing: 6

                                        Text {
                                            text: "😊"
                                            font.pixelSize: 16
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 32
                                            radius: 16
                                            color: "#2A3942"

                                            Text {
                                                anchors.verticalCenter: parent.verticalCenter
                                                anchors.left: parent.left
                                                anchors.leftMargin: 10
                                                text: "Type a message"
                                                color: "#8696A0"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: 11
                                            }
                                        }

                                        Text {
                                            text: "📎"
                                            font.pixelSize: 15
                                        }

                                        // Circular WhatsApp Green Send Button
                                        Rectangle {
                                            width: 32
                                            height: 32
                                            radius: 16
                                            color: sendMouse.containsMouse ? "#00B894" : "#00A884"

                                            Text {
                                                anchors.centerIn: parent
                                                text: "➤"
                                                color: "#FFFFFF"
                                                font.pixelSize: 13
                                            }

                                            MouseArea {
                                                id: sendMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.dispatchSingleMessage()
                                            }
                                        }
                                    }
                                }

                                // 5. Smartphone Bottom Home Indicator Bar
                                Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 14
                                    color: "#182229"

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 100
                                        height: 3
                                        radius: 2
                                        color: "#8696A0"
                                    }
                                }
                            }
                        }

                        // Bottom Action Buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingMD

                            PrimaryButton {
                                Layout.fillWidth: true
                                text: `⚡ Send WhatsApp to ${root.previewStudent ? root.previewStudent.name : 'Recipient'}`
                                iconName: "whatsapp"
                                customHeight: 44
                                onClicked: root.dispatchSingleMessage()
                            }

                            SecondaryButton {
                                Layout.fillWidth: true
                                text: `Start Batch Dispatch (${root.recipientsList.length} In Queue)`
                                iconName: "messaging"
                                customHeight: 44
                                onClicked: root.dispatchBatchQueue()
                            }
                        }
                    }
                }
            }

            // 3. Right Panel: Targeted Recipients & Audience Filter
            Rectangle {
                Layout.preferredWidth: 420
                Layout.minimumWidth: 380
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMD
                    spacing: Theme.spacingSM

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: `Recipients (${root.filteredRecipients.length})`
                            color: Theme.textPrimary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontBody
                            font.weight: Theme.weightBold
                        }
                    }

                    SearchBar {
                        placeholderText: "Search recipient name, phone, course..."
                        Layout.fillWidth: true
                        onSearchChanged: query => {
                            root.recipientSearchQuery = query;
                            root.applyRecipientFilter();
                        }
                    }

                    // Audience Selector
                    FilterBar {
                        options: ["Pending Fees", "All Active", "Specific Course"]
                        selectedOption: root.selectedAudience === "All" ? "All Active" : root.selectedAudience
                        onSelectionChanged: opt => {
                            root.selectedAudience = (opt === "All Active") ? "All" : opt;
                            root.refreshRecipients();
                        }
                    }

                    ComboBox {
                        visible: root.selectedAudience === "Specific Course"
                        Layout.fillWidth: true
                        model: root.coursesList
                        onCurrentTextChanged: {
                            root.selectedCourseFilter = currentText;
                            root.refreshRecipients();
                        }
                    }

                    DataTable {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: root.filteredRecipients
                        showPagination: false

                        columns: [
                            { "title": "Recipient", "role": "name", "width": 140, "fill": true, "isPrimary": true },
                            { "title": "Last Paid", "role": "last_paid_date_str", "subtitleRole": "days_ago_str", "width": 105, "isDateWithSubtitle": true },
                            { "title": "Dues", "role": "balance_due", "width": 75, "isCurrency": true, "alignRight": true },
                            { "title": "Send", "role": "actions", "width": 36, "isAction": true, "actions": ["whatsapp"], "alignRight": true }
                        ]

                        onRowClicked: (rowData, index) => {
                            root.previewStudent = rowData;
                            root.updatePreview();
                        }

                        onRowDoubleClicked: (rowData, index) => {
                            if (typeof studentDetailsPage !== "undefined") {
                                studentDetailsPage.loadStudent(rowData.id);
                                studentDetailsPage.activeTab = "Fee Installments";
                            }
                            crmBridge.navigateTo("StudentDetails");
                        }

                        onRowAction: (action, rowData, index) => {
                            if (action === "whatsapp") {
                                var ok = messagingBridge.sendWhatsAppToStudent(rowData.id, root.currentTemplateText, true);
                                if (ok) {
                                    crmBridge.showToast(`Message launched for ${rowData.name}`, "success", "WhatsApp Sent");
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // New / Edit Template Drawer
    DrawerPanel {
        id: templateEditorDrawer
        title: editingTemplateId ? "Edit Message Template" : "Create Message Template"
        primaryActionText: "Save Template"
        property string editingTemplateId: ""

        function openDrawer(tmpl) {
            editingTemplateId = tmpl ? String(tmpl.id) : "";
            tmplTitleField.text = tmpl ? tmpl.title : "";
            tmplCatField.text = tmpl ? tmpl.category : "Fees";
            tmplContentField.text = tmpl ? tmpl.content : "";
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!tmplTitleField.text.trim()) {
                crmBridge.showToast("Template title is required.", "warning", "Validation Error");
                return;
            }

            var payload = {
                "id": editingTemplateId ? editingTemplateId : undefined,
                "title": tmplTitleField.text.trim(),
                "category": tmplCatField.text.trim(),
                "content": tmplContentField.text.trim(),
                "is_default": true
            };

            var res = messagingBridge.saveTemplate(JSON.stringify(payload));
            if (res.success) {
                isOpen = false;
                root.refresh();
                crmBridge.showToast(res.message, "success", "Saved");
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingMD

            FormField {
                id: tmplTitleField
                label: "Template Title"
                required: true
                placeholder: "e.g. Urgent Overdue Reminder"
            }

            FormField {
                id: tmplCatField
                label: "Category"
                placeholder: "e.g. Fees / Admissions / Batches"
            }

            FormField {
                id: tmplContentField
                label: "Message Body (with Spintax & Merge Tags)"
                isMultiline: true
                customHeight: 150
                placeholder: "{Dear|Hello} {name}, your balance of ₹{balance_due} is pending..."
            }
        }
    }
}
