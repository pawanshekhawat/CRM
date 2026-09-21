import QtQuick
import "../theme"

Item {
    id: root

    property string name: "circle"
    property int size: 18
    property color color: Theme.textSecondary

    width: size
    height: size

    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.FramebufferObject

        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            ctx.clearRect(0, 0, width, height);

            ctx.strokeStyle = root.color;
            ctx.fillStyle = root.color;
            ctx.lineWidth = Math.max(1.5, root.size / 10);
            ctx.lineCap = "round";
            ctx.lineJoin = "round";

            var s = root.size;
            var p = s * 0.12; // padding
            var w = s - (p * 2);
            var h = s - (p * 2);

            switch (root.name) {
                case "dashboard":
                    // 4 squares
                    var hw = w / 2 - 1.5;
                    var hh = h / 2 - 1.5;
                    ctx.strokeRect(p, p, hw, hh);
                    ctx.strokeRect(p + hw + 3, p, hw, hh);
                    ctx.strokeRect(p, p + hh + 3, hw, hh);
                    ctx.strokeRect(p + hw + 3, p + hh + 3, hw, hh);
                    break;

                case "menu":
                case "hamburger":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.1, p + h * 0.25);
                    ctx.lineTo(p + w * 0.9, p + h * 0.25);
                    ctx.moveTo(p + w * 0.1, p + h * 0.5);
                    ctx.lineTo(p + w * 0.9, p + h * 0.5);
                    ctx.moveTo(p + w * 0.1, p + h * 0.75);
                    ctx.lineTo(p + w * 0.9, p + h * 0.75);
                    ctx.stroke();
                    break;

                case "sidebar":
                    ctx.strokeRect(p, p, w, h);
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.35, p);
                    ctx.lineTo(p + w * 0.35, p + h);
                    ctx.stroke();
                    break;

                case "students":
                case "users":
                    // 2 user silhouettes
                    ctx.beginPath();
                    ctx.arc(p + w * 0.38, p + h * 0.3, w * 0.2, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(p + w * 0.38, p + h * 0.85, w * 0.32, Math.PI, 0, false);
                    ctx.stroke();
                    // second user offset
                    ctx.beginPath();
                    ctx.arc(p + w * 0.72, p + h * 0.25, w * 0.15, -Math.PI * 0.5, Math.PI * 0.8);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(p + w * 0.75, p + h * 0.8, w * 0.22, Math.PI * 1.1, 0, false);
                    ctx.stroke();
                    break;

                case "user":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.32, w * 0.24, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.95, w * 0.42, Math.PI, 0, false);
                    ctx.stroke();
                    break;

                case "courses":
                case "book":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.5, p + h * 0.2);
                    ctx.lineTo(p + w * 0.5, p + h * 0.95);
                    ctx.stroke();
                    // Left page
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.5, p + h * 0.2);
                    ctx.quadraticCurveTo(p + w * 0.25, p + h * 0.1, p, p + h * 0.2);
                    ctx.lineTo(p, p + h * 0.85);
                    ctx.quadraticCurveTo(p + w * 0.25, p + h * 0.75, p + w * 0.5, p + h * 0.95);
                    ctx.stroke();
                    // Right page
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.5, p + h * 0.2);
                    ctx.quadraticCurveTo(p + w * 0.75, p + h * 0.1, p + w, p + h * 0.2);
                    ctx.lineTo(p + w, p + h * 0.85);
                    ctx.quadraticCurveTo(p + w * 0.75, p + h * 0.75, p + w * 0.5, p + h * 0.95);
                    ctx.stroke();
                    break;

                case "batches":
                case "calendar":
                    ctx.strokeRect(p, p + h * 0.15, w, h * 0.85);
                    ctx.beginPath();
                    ctx.moveTo(p, p + h * 0.4);
                    ctx.lineTo(p + w, p + h * 0.4);
                    ctx.moveTo(p + w * 0.3, p);
                    ctx.lineTo(p + w * 0.3, p + h * 0.25);
                    ctx.moveTo(p + w * 0.7, p);
                    ctx.lineTo(p + w * 0.7, p + h * 0.25);
                    ctx.stroke();
                    break;

                case "fees":
                case "finance":
                case "dollar-sign":
                    // Rupee symbol
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.2, p + h * 0.15);
                    ctx.lineTo(p + w * 0.8, p + h * 0.15);
                    ctx.moveTo(p + w * 0.2, p + h * 0.38);
                    ctx.lineTo(p + w * 0.75, p + h * 0.38);
                    ctx.moveTo(p + w * 0.4, p + h * 0.15);
                    ctx.bezierCurveTo(p + w * 0.85, p + h * 0.15, p + w * 0.85, p + h * 0.55, p + w * 0.35, p + h * 0.55);
                    ctx.lineTo(p + w * 0.8, p + h * 0.95);
                    ctx.stroke();
                    break;

                case "staff":
                case "briefcase":
                    ctx.strokeRect(p, p + h * 0.3, w, h * 0.7);
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.3, p + h * 0.3);
                    ctx.lineTo(p + w * 0.3, p + h * 0.15);
                    ctx.lineTo(p + w * 0.7, p + h * 0.15);
                    ctx.lineTo(p + w * 0.7, p + h * 0.3);
                    ctx.stroke();
                    break;

                case "messaging":
                case "message":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.1, p + h * 0.1);
                    ctx.lineTo(p + w * 0.9, p + h * 0.1);
                    ctx.lineTo(p + w * 0.9, p + h * 0.7);
                    ctx.lineTo(p + w * 0.45, p + h * 0.7);
                    ctx.lineTo(p + w * 0.2, p + h * 0.95);
                    ctx.lineTo(p + w * 0.2, p + h * 0.7);
                    ctx.lineTo(p + w * 0.1, p + h * 0.7);
                    ctx.closePath();
                    ctx.stroke();
                    break;

                case "reports":
                case "chart":
                    // Bar chart
                    ctx.beginPath();
                    ctx.moveTo(p, p + h);
                    ctx.lineTo(p + w, p + h);
                    ctx.stroke();
                    ctx.strokeRect(p + w * 0.15, p + h * 0.5, w * 0.18, h * 0.5);
                    ctx.strokeRect(p + w * 0.42, p + h * 0.25, w * 0.18, h * 0.75);
                    ctx.strokeRect(p + w * 0.69, p + h * 0.1, w * 0.18, h * 0.9);
                    break;

                case "documents":
                case "file":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.15, p);
                    ctx.lineTo(p + w * 0.6, p);
                    ctx.lineTo(p + w * 0.85, p + h * 0.25);
                    ctx.lineTo(p + w * 0.85, p + h);
                    ctx.lineTo(p + w * 0.15, p + h);
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.6, p);
                    ctx.lineTo(p + w * 0.6, p + h * 0.25);
                    ctx.lineTo(p + w * 0.85, p + h * 0.25);
                    ctx.stroke();
                    break;

                case "settings":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.5, w * 0.2, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    for (var i = 0; i < 6; i++) {
                        var ang = i * Math.PI / 3;
                        var r1 = w * 0.32;
                        var r2 = w * 0.48;
                        ctx.moveTo(p + w * 0.5 + Math.cos(ang) * r1, p + h * 0.5 + Math.sin(ang) * r1);
                        ctx.lineTo(p + w * 0.5 + Math.cos(ang) * r2, p + h * 0.5 + Math.sin(ang) * r2);
                    }
                    ctx.stroke();
                    break;

                case "search":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.4, p + h * 0.4, w * 0.32, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.63, p + h * 0.63);
                    ctx.lineTo(p + w * 0.95, p + h * 0.95);
                    ctx.stroke();
                    break;

                case "filter":
                    ctx.beginPath();
                    ctx.moveTo(p, p + h * 0.1);
                    ctx.lineTo(p + w, p + h * 0.1);
                    ctx.lineTo(p + w * 0.6, p + h * 0.55);
                    ctx.lineTo(p + w * 0.6, p + h * 0.95);
                    ctx.lineTo(p + w * 0.4, p + h * 0.8);
                    ctx.lineTo(p + w * 0.4, p + h * 0.55);
                    ctx.closePath();
                    ctx.stroke();
                    break;

                case "plus":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.5, p);
                    ctx.lineTo(p + w * 0.5, p + h);
                    ctx.moveTo(p, p + h * 0.5);
                    ctx.lineTo(p + w, p + h * 0.5);
                    ctx.stroke();
                    break;

                case "check":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.15, p + h * 0.55);
                    ctx.lineTo(p + w * 0.4, p + h * 0.8);
                    ctx.lineTo(p + w * 0.9, p + h * 0.2);
                    ctx.stroke();
                    break;

                case "eye":
                case "view":
                    ctx.beginPath();
                    ctx.moveTo(p, p + h * 0.5);
                    ctx.quadraticCurveTo(p + w * 0.5, p + h * 0.1, p + w, p + h * 0.5);
                    ctx.quadraticCurveTo(p + w * 0.5, p + h * 0.9, p, p + h * 0.5);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.5, w * 0.18, 0, Math.PI * 2);
                    ctx.stroke();
                    break;

                case "x":
                case "close":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.2, p + h * 0.2);
                    ctx.lineTo(p + w * 0.8, p + h * 0.8);
                    ctx.moveTo(p + w * 0.8, p + h * 0.2);
                    ctx.lineTo(p + w * 0.2, p + h * 0.8);
                    ctx.stroke();
                    break;

                case "chevron-left":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.65, p + h * 0.15);
                    ctx.lineTo(p + w * 0.3, p + h * 0.5);
                    ctx.lineTo(p + w * 0.65, p + h * 0.85);
                    ctx.stroke();
                    break;

                case "chevron-right":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.35, p + h * 0.15);
                    ctx.lineTo(p + w * 0.7, p + h * 0.5);
                    ctx.lineTo(p + w * 0.35, p + h * 0.85);
                    ctx.stroke();
                    break;

                case "chevron-down":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.2, p + h * 0.35);
                    ctx.lineTo(p + w * 0.5, p + h * 0.65);
                    ctx.lineTo(p + w * 0.8, p + h * 0.35);
                    ctx.stroke();
                    break;

                case "chevron-up":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.2, p + h * 0.65);
                    ctx.lineTo(p + w * 0.5, p + h * 0.35);
                    ctx.lineTo(p + w * 0.8, p + h * 0.65);
                    ctx.stroke();
                    break;

                case "sort":
                case "arrow-up-down":
                    ctx.beginPath();
                    // Up arrow on left
                    ctx.moveTo(p + w * 0.32, p + h * 0.8);
                    ctx.lineTo(p + w * 0.32, p + h * 0.2);
                    ctx.lineTo(p + w * 0.16, p + h * 0.36);
                    ctx.moveTo(p + w * 0.32, p + h * 0.2);
                    ctx.lineTo(p + w * 0.48, p + h * 0.36);
                    // Down arrow on right
                    ctx.moveTo(p + w * 0.68, p + h * 0.2);
                    ctx.lineTo(p + w * 0.68, p + h * 0.8);
                    ctx.lineTo(p + w * 0.52, p + h * 0.64);
                    ctx.moveTo(p + w * 0.68, p + h * 0.8);
                    ctx.lineTo(p + w * 0.84, p + h * 0.64);
                    ctx.stroke();
                    break;

                case "refresh":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.5, w * 0.38, -Math.PI * 0.2, Math.PI * 1.3);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.85, p + h * 0.15);
                    ctx.lineTo(p + w * 0.88, p + h * 0.42);
                    ctx.lineTo(p + w * 0.6, p + h * 0.42);
                    ctx.stroke();
                    break;

                case "download":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.5, p);
                    ctx.lineTo(p + w * 0.5, p + h * 0.65);
                    ctx.lineTo(p + w * 0.25, p + h * 0.4);
                    ctx.moveTo(p + w * 0.5, p + h * 0.65);
                    ctx.lineTo(p + w * 0.75, p + h * 0.4);
                    ctx.moveTo(p + w * 0.1, p + h * 0.95);
                    ctx.lineTo(p + w * 0.9, p + h * 0.95);
                    ctx.stroke();
                    break;

                case "edit":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.15, p + h * 0.85);
                    ctx.lineTo(p + w * 0.35, p + h * 0.85);
                    ctx.lineTo(p + w * 0.85, p + h * 0.35);
                    ctx.lineTo(p + w * 0.65, p + h * 0.15);
                    ctx.lineTo(p + w * 0.15, p + h * 0.65);
                    ctx.closePath();
                    ctx.stroke();
                    break;

                case "trash":
                    ctx.strokeRect(p + w * 0.2, p + h * 0.28, w * 0.6, h * 0.72);
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.1, p + h * 0.28);
                    ctx.lineTo(p + w * 0.9, p + h * 0.28);
                    ctx.moveTo(p + w * 0.35, p + h * 0.28);
                    ctx.lineTo(p + w * 0.35, p + h * 0.12);
                    ctx.lineTo(p + w * 0.65, p + h * 0.12);
                    ctx.lineTo(p + w * 0.65, p + h * 0.28);
                    ctx.stroke();
                    break;

                case "whatsapp":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.45, w * 0.4, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.22, p + h * 0.73);
                    ctx.lineTo(p + w * 0.15, p + h * 0.92);
                    ctx.lineTo(p + w * 0.34, p + h * 0.84);
                    ctx.stroke();
                    break;

                case "zoom-in":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.42, p + h * 0.42, w * 0.32, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.65, p + h * 0.65);
                    ctx.lineTo(p + w * 0.95, p + h * 0.95);
                    ctx.stroke();
                    // plus
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.42, p + h * 0.26);
                    ctx.lineTo(p + w * 0.42, p + h * 0.58);
                    ctx.moveTo(p + w * 0.26, p + h * 0.42);
                    ctx.lineTo(p + w * 0.58, p + h * 0.42);
                    ctx.stroke();
                    break;

                case "zoom-out":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.42, p + h * 0.42, w * 0.32, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.65, p + h * 0.65);
                    ctx.lineTo(p + w * 0.95, p + h * 0.95);
                    ctx.stroke();
                    // minus
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.26, p + h * 0.42);
                    ctx.lineTo(p + w * 0.58, p + h * 0.42);
                    ctx.stroke();
                    break;

                case "rotate":
                case "rotate-cw":
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.5, w * 0.38, -Math.PI * 0.8, Math.PI * 0.7);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.8, p + h * 0.7);
                    ctx.lineTo(p + w * 0.95, p + h * 0.85);
                    ctx.lineTo(p + w * 0.7, p + h * 0.95);
                    ctx.stroke();
                    break;

                case "fullscreen":
                case "expand":
                    var c = w * 0.28;
                    // Top-left
                    ctx.beginPath();
                    ctx.moveTo(p, p + c);
                    ctx.lineTo(p, p);
                    ctx.lineTo(p + c, p);
                    ctx.stroke();
                    // Top-right
                    ctx.beginPath();
                    ctx.moveTo(p + w - c, p);
                    ctx.lineTo(p + w, p);
                    ctx.lineTo(p + w, p + c);
                    ctx.stroke();
                    // Bottom-left
                    ctx.beginPath();
                    ctx.moveTo(p, p + h - c);
                    ctx.lineTo(p, p + h);
                    ctx.lineTo(p + c, p + h);
                    ctx.stroke();
                    // Bottom-right
                    ctx.beginPath();
                    ctx.moveTo(p + w - c, p + h);
                    ctx.lineTo(p + w, p + h);
                    ctx.lineTo(p + w, p + h - c);
                    ctx.stroke();
                    break;

                case "fit":
                case "fit-screen":
                    ctx.strokeRect(p + w * 0.1, p + h * 0.15, w * 0.8, h * 0.7);
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.3, p + h * 0.5);
                    ctx.lineTo(p + w * 0.7, p + h * 0.5);
                    ctx.stroke();
                    break;

                case "document":
                case "file":
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.15, p);
                    ctx.lineTo(p + w * 0.6, p);
                    ctx.lineTo(p + w * 0.85, p + h * 0.25);
                    ctx.lineTo(p + w * 0.85, p + h);
                    ctx.lineTo(p + w * 0.15, p + h);
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.6, p);
                    ctx.lineTo(p + w * 0.6, p + h * 0.25);
                    ctx.lineTo(p + w * 0.85, p + h * 0.25);
                    ctx.stroke();
                    break;

                case "image":
                case "picture":
                    ctx.strokeRect(p, p, w, h);
                    ctx.beginPath();
                    ctx.arc(p + w * 0.3, p + h * 0.35, w * 0.1, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(p, p + h * 0.8);
                    ctx.lineTo(p + w * 0.35, p + h * 0.45);
                    ctx.lineTo(p + w * 0.65, p + h * 0.7);
                    ctx.lineTo(p + w * 0.85, p + h * 0.55);
                    ctx.lineTo(p + w, p + h * 0.7);
                    ctx.stroke();
                    break;

                case "whatsapp":
                case "message":
                case "messaging":
                case "chat":
                    // Smooth Chat bubble with speech pointer
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.46, w * 0.4, -Math.PI * 0.15, Math.PI * 1.22);
                    ctx.lineTo(p + w * 0.14, p + h * 0.94);
                    ctx.lineTo(p + w * 0.4, p + h * 0.82);
                    ctx.closePath();
                    ctx.stroke();
                    // Inner conversation lines
                    ctx.beginPath();
                    ctx.moveTo(p + w * 0.32, p + h * 0.4);
                    ctx.lineTo(p + w * 0.68, p + h * 0.4);
                    ctx.moveTo(p + w * 0.32, p + h * 0.55);
                    ctx.lineTo(p + w * 0.56, p + h * 0.55);
                    ctx.stroke();
                    break;

                default:
                    ctx.beginPath();
                    ctx.arc(p + w * 0.5, p + h * 0.5, w * 0.35, 0, Math.PI * 2);
                    ctx.stroke();
                    break;
            }
        }
    }

    onColorChanged: canvas.requestPaint()
    onNameChanged: canvas.requestPaint()
    onSizeChanged: canvas.requestPaint()
}
