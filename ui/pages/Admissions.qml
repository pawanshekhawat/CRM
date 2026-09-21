import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    property var coursesList: []
    property var staffList: []
    property string editingStudentId: ""
    property string editingStudentIdNo: ""

    function loadDropdowns() {
        if (typeof coursesBridge !== "undefined") {
            coursesList = coursesBridge.getCourseNames();
        }
        if (typeof staffBridge !== "undefined") {
            var rawStaff = staffBridge.getStaffNames() || [];
            staffList = [{"id": "", "name": "— Not Selected (Optional) —"}].concat(rawStaff);
        }
    }

    function resetForm() {
        root.editingStudentId = "";
        root.editingStudentIdNo = "";
        nameField.text = "";
        mobileField.text = "";
        emailField.text = "";
        fatherNameField.text = "";
        fatherContactField.text = "";
        motherNameField.text = "";
        dobField.text = "";
        aadharField.text = "";
        altPhoneField.text = "";
        admissionDateField.text = Qt.formatDate(new Date(), "yyyy-MM-dd");
        collegeField.text = "";
        yearSemField.text = "";
        fatherOccField.text = "";
        courseFeeField.text = "0";
        discountField.text = "0";
        netFeeField.text = "0";
        initialPaidField.text = "0";
        addressField.text = "";
        districtField.text = "";
        stateField.text = "Rajasthan";
        pinField.text = "";
        if (courseCombo.count > 0) courseCombo.currentIndex = 0;
        if (mentorCombo.count > 0) mentorCombo.currentIndex = 0;
    }

    function loadStudentForEdit(studentId) {
        if (!studentId) return;
        root.loadDropdowns();
        root.editingStudentId = String(studentId);

        if (typeof studentsBridge !== "undefined") {
            var s = studentsBridge.getStudentById(String(studentId));
            if (s && s.id) {
                root.editingStudentIdNo = s.id_no || "";
                nameField.text = s.name || "";
                mobileField.text = s.mobile_no || "";
                emailField.text = s.email && s.email !== "N/A" ? s.email : "";
                fatherNameField.text = s.father_name && s.father_name !== "N/A" ? s.father_name : "";
                fatherContactField.text = s.father_contact && s.father_contact !== "N/A" ? s.father_contact : "";
                motherNameField.text = s.mother_name && s.mother_name !== "N/A" ? s.mother_name : "";
                dobField.text = s.dob && s.dob !== "N/A" ? s.dob : "";
                aadharField.text = s.aadhar_no && s.aadhar_no !== "N/A" ? s.aadhar_no : "";
                altPhoneField.text = s.alternate_contact && s.alternate_contact !== "N/A" ? s.alternate_contact : "";
                admissionDateField.text = s.admission_date && s.admission_date !== "N/A" ? s.admission_date : Qt.formatDate(new Date(), "yyyy-MM-dd");
                collegeField.text = s.college_school && s.college_school !== "N/A" ? s.college_school : "";
                yearSemField.text = s.year_semester && s.year_semester !== "N/A" ? s.year_semester : "";
                fatherOccField.text = s.father_occupation && s.father_occupation !== "N/A" ? s.father_occupation : "";
                courseFeeField.text = String(s.total_course_fee || 0);
                discountField.text = String(s.scholarship_discount || 0);
                netFeeField.text = String(s.net_payable_fee || 0);
                initialPaidField.text = String(s.total_paid_fee || 0);
                addressField.text = s.permanent_address && s.permanent_address !== "N/A" ? s.permanent_address : "";
                districtField.text = s.district && s.district !== "N/A" ? s.district : "";
                stateField.text = s.state && s.state !== "N/A" ? s.state : "Rajasthan";
                pinField.text = s.pin_code && s.pin_code !== "N/A" ? s.pin_code : "";

                // Set course combo
                if (s.course_name) {
                    var idx = courseCombo.indexOfValue(s.course_name);
                    if (idx >= 0) courseCombo.currentIndex = idx;
                }

                // Set mentor combo
                if (s.assigned_staff_id) {
                    var mIdx = mentorCombo.indexOfValue(String(s.assigned_staff_id));
                    if (mIdx >= 0) {
                        mentorCombo.currentIndex = mIdx;
                    } else {
                        mentorCombo.currentIndex = 0;
                    }
                } else {
                    mentorCombo.currentIndex = 0;
                }
            }
        }
    }

    Component.onCompleted: loadDropdowns()

    Item {
        width: root.availableWidth
        implicitHeight: mainCol.implicitHeight + (Theme.spacingLG * 2)

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: Theme.spacingLG
            spacing: Theme.spacingLG

            // Header
            PageHeader {
                title: root.editingStudentId ? `Edit Student — ${nameField.text || 'Profile'} (${root.editingStudentIdNo})` : "Student Admission & Enrollment"
                subtitle: root.editingStudentId ? "Update student personal particulars, academic records, and fee configuration" : "Enroll a new candidate, assign academic program, and configure fee payment structure"

                SecondaryButton {
                    text: root.editingStudentId ? "Back to Student Profile" : "Back to Students"
                    iconName: "chevron-left"
                    onClicked: {
                        if (root.editingStudentId) {
                            if (typeof studentDetailsPage !== "undefined") {
                                studentDetailsPage.loadStudent(root.editingStudentId);
                            }
                            crmBridge.navigateTo("StudentDetails");
                        } else {
                            crmBridge.navigateTo("Students");
                        }
                    }
                }

                PrimaryButton {
                    text: root.editingStudentId ? "Update Student Details" : "Save & Generate Admission Slip"
                    iconName: "check"
                    onClicked: root.submitAdmission(!root.editingStudentId)
                }
            }

            // Form Container Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: formLayout.implicitHeight + (Theme.spacingLG * 2)
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    id: formLayout
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingXL

                    // Section 1: Personal & Identification
                    FormSection {
                        title: "1. Personal & Contact Information"
                        description: "Primary student particulars and official contact channels"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField {
                                id: nameField
                                label: "Full Name"
                                required: true
                                placeholder: "e.g. Rahul Sharma"
                            }

                            FormField {
                                id: mobileField
                                label: "Mobile Number"
                                required: true
                                placeholder: "10-digit mobile number"
                            }

                            FormField {
                                id: emailField
                                label: "Email Address"
                                placeholder: "student@example.com"
                            }

                            FormField {
                                id: fatherNameField
                                label: "Father's Name"
                                required: true
                                placeholder: "Father's full name"
                            }

                            FormField {
                                id: fatherContactField
                                label: "Father / Guardian Contact"
                                placeholder: "Guardian phone"
                            }

                            FormField {
                                id: motherNameField
                                label: "Mother's Name"
                                placeholder: "Mother's full name"
                            }

                            FormField {
                                id: dobField
                                label: "Date of Birth"
                                placeholder: "YYYY-MM-DD"
                            }

                            FormField {
                                id: aadharField
                                label: "Aadhar Number"
                                placeholder: "12-digit Aadhar"
                            }

                            FormField {
                                id: altPhoneField
                                label: "Alternate Phone"
                                placeholder: "Alternate contact"
                            }
                        }
                    }

                    // Section 2: Academic Program & Faculty Mentor
                    FormSection {
                        title: "2. Academic Program & Course"
                        description: "Select training course and assign faculty mentor"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            ColumnLayout {
                                spacing: 4
                                Layout.fillWidth: true

                                RowLayout {
                                    Text { text: "Course Program"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall; font.weight: Theme.weightMedium }
                                    Text { text: "*"; color: Theme.danger; font.pixelSize: Theme.fontSmall; font.weight: Theme.weightBold }
                                }

                                ComboBox {
                                    id: courseCombo
                                    Layout.fillWidth: true
                                    model: root.coursesList
                                    onCurrentTextChanged: {
                                        if (!root.editingStudentId && typeof coursesBridge !== "undefined" && currentText) {
                                            var fee = coursesBridge.getStandardFeeForCourse(currentText);
                                            courseFeeField.text = String(fee);
                                            root.recalculateNet();
                                        }
                                    }
                                }
                            }

                            FormField {
                                id: admissionDateField
                                label: "Admission Date"
                                text: Qt.formatDate(new Date(), "yyyy-MM-dd")
                                placeholder: "YYYY-MM-DD"
                            }

                            ColumnLayout {
                                spacing: 4
                                Layout.fillWidth: true

                                Text { text: "Faculty Mentor (Optional)"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall; font.weight: Theme.weightMedium }

                                ComboBox {
                                    id: mentorCombo
                                    Layout.fillWidth: true
                                    textRole: "name"
                                    valueRole: "id"
                                    model: root.staffList
                                    currentIndex: 0
                                }
                            }

                            FormField {
                                id: collegeField
                                label: "College / School"
                                placeholder: "e.g. Government Engineering College"
                            }

                            FormField {
                                id: yearSemField
                                label: "Year / Semester"
                                placeholder: "e.g. 3rd Year / 6th Sem"
                            }

                            FormField {
                                id: fatherOccField
                                label: "Father's Occupation"
                                placeholder: "e.g. Business / Service"
                            }
                        }
                    }

                    // Section 3: Fee Structure & Initial Token
                    FormSection {
                        title: "3. Fee Structure & Payment Installments"
                        description: "Configure standard course fees, scholarships, and payment plan"

                        GridLayout {
                            columns: 4
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField {
                                id: courseFeeField
                                label: "Standard Course Fee"
                                prefix: "₹"
                                text: "0"
                                onValueModified: root.recalculateNet()
                            }

                            FormField {
                                id: discountField
                                label: "Scholarship / Discount"
                                prefix: "₹"
                                text: "0"
                                onValueModified: root.recalculateNet()
                            }

                            FormField {
                                id: netFeeField
                                label: "Net Payable Fee"
                                prefix: "₹"
                                text: "0"
                                readOnly: true
                            }

                            FormField {
                                id: initialPaidField
                                label: root.editingStudentId ? "Total Paid (Recorded)" : "Initial Amount Paid (Token)"
                                prefix: "₹"
                                text: "0"
                                readOnly: root.editingStudentId !== ""
                            }
                        }
                    }

                    // Section 4: Address
                    FormSection {
                        title: "4. Permanent Address"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField {
                                id: addressField
                                label: "Street Address"
                                placeholder: "Complete permanent address"
                                Layout.columnSpan: 2
                            }

                            FormField {
                                id: districtField
                                label: "District"
                                placeholder: "e.g. Jaipur"
                            }

                            FormField {
                                id: stateField
                                label: "State"
                                text: "Rajasthan"
                            }

                            FormField {
                                id: pinField
                                label: "PIN Code"
                                placeholder: "e.g. 302001"
                            }
                        }
                    }

                    // Action Bar Bottom
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.topMargin: Theme.spacingMD
                        spacing: Theme.spacingMD

                        SecondaryButton {
                            text: "Cancel"
                            onClicked: {
                                if (root.editingStudentId) {
                                    if (typeof studentDetailsPage !== "undefined") {
                                        studentDetailsPage.loadStudent(root.editingStudentId);
                                    }
                                    crmBridge.navigateTo("StudentDetails");
                                } else {
                                    crmBridge.navigateTo("Students");
                                }
                            }
                        }

                        Item { Layout.fillWidth: true }

                        PrimaryButton {
                            text: root.editingStudentId ? "Update Student Details" : "Save & Generate Admission Slip"
                            iconName: "check"
                            onClicked: root.submitAdmission(!root.editingStudentId)
                        }
                    }
                }
            }
        }
    }

    function recalculateNet() {
        var total = parseFloat(courseFeeField.text) || 0;
        var discount = parseFloat(discountField.text) || 0;
        var net = Math.max(0, total - discount);
        netFeeField.text = String(net);
    }

    function submitAdmission(printSlip) {
        if (!nameField.text.trim()) {
            crmBridge.showToast("Student name is mandatory.", "warning", "Validation Error");
            return;
        }
        if (!mobileField.text.trim()) {
            crmBridge.showToast("Student mobile number is mandatory.", "warning", "Validation Error");
            return;
        }

        var totalFee = parseFloat(courseFeeField.text) || 0;
        var discount = parseFloat(discountField.text) || 0;
        var netFee = parseFloat(netFeeField.text) || 0;
        var initPaid = parseFloat(initialPaidField.text) || 0;

        var payload = {
            "name": nameField.text.trim(),
            "mobile_no": mobileField.text.trim(),
            "email": emailField.text.trim(),
            "father_name": fatherNameField.text.trim(),
            "mother_name": motherNameField.text.trim(),
            "father_contact": fatherContactField.text.trim(),
            "dob": dobField.text.trim(),
            "aadhar_no": aadharField.text.trim(),
            "alternate_contact": altPhoneField.text.trim(),
            "course_name": courseCombo.currentText,
            "assigned_staff_id": (mentorCombo.currentIndex > 0 && mentorCombo.currentValue) ? mentorCombo.currentValue : null,
            "admission_date": admissionDateField.text.trim(),
            "college_school": collegeField.text.trim(),
            "year_semester": yearSemField.text.trim(),
            "father_occupation": fatherOccField.text.trim(),
            "permanent_address": addressField.text.trim(),
            "district": districtField.text.trim(),
            "state": stateField.text.trim(),
            "pin_code": pinField.text.trim(),
            "total_course_fee": totalFee,
            "scholarship_discount": discount,
            "net_payable_fee": netFee,
            "status": "Active"
        };

        if (root.editingStudentId) {
            payload["id"] = root.editingStudentId;
        } else {
            var installments = [];
            if (initPaid > 0) {
                installments.push({
                    "installment_no": 1,
                    "due_amount": initPaid,
                    "paid_amount": initPaid,
                    "payment_date": Qt.formatDate(new Date(), "yyyy-MM-dd"),
                    "payment_mode": "Cash",
                    "receipt_no": `REC-${Date.now().toString().slice(-6)}`,
                    "remarks": "Admission token payment"
                });
            }

            var remaining = netFee - initPaid;
            if (remaining > 0) {
                installments.push({
                    "installment_no": installments.length + 1,
                    "due_amount": remaining,
                    "paid_amount": 0,
                    "due_date": Qt.formatDate(new Date(Date.now() + 30*24*3600*1000), "yyyy-MM-dd"),
                    "remarks": "Second installment"
                });
            }

            payload["total_paid_fee"] = initPaid;
            payload["balance_due"] = remaining;
            payload["fee_installments"] = installments;
        }

        var res = studentsBridge.saveStudent(JSON.stringify(payload), "", []);
        if (res.success) {
            crmBridge.showToast(res.message, "success", root.editingStudentId ? "Updated" : "Enrolled");
            var sid = res.id || root.editingStudentId;
            if (printSlip && sid > 0) {
                var pdf = studentsBridge.generateAdmissionPdf(sid);
                if (pdf) {
                    reportsBridge.openDocument(pdf);
                }
            }
            if (root.editingStudentId) {
                if (typeof studentDetailsPage !== "undefined") {
                    studentDetailsPage.loadStudent(sid);
                }
                crmBridge.navigateTo("StudentDetails");
            } else {
                crmBridge.navigateTo("Students");
            }
        } else {
            crmBridge.showToast(res.message, "error", "Saving Failed");
        }
    }
}
