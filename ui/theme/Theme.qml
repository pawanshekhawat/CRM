import QtQuick

pragma Singleton

QtObject {
    id: theme

    // Current active theme mode: "dark" (default) or "light"
    property string mode: "dark"
    property bool isDark: mode === "dark"

    // --- Color Palette Tokens ---
    // Backgrounds & Surfaces
    readonly property color background: isDark ? "#0B0E14" : "#F8FAFC"
    readonly property color surface: isDark ? "#121824" : "#FFFFFF"
    readonly property color surfaceElevated: isDark ? "#1A2234" : "#F1F5F9"
    readonly property color surfaceHover: isDark ? "#222D44" : "#E2E8F0"
    readonly property color surfaceActive: isDark ? "#2A3752" : "#CBD5E1"

    // Borders
    readonly property color border: isDark ? "#243048" : "#E2E8F0"
    readonly property color borderSubtle: isDark ? "#1C2638" : "#F1F5F9"
    readonly property color borderFocus: isDark ? "#3B82F6" : "#2563EB"

    // Text & Content Hierarchy
    readonly property color textPrimary: isDark ? "#F8FAFC" : "#0F172A"
    readonly property color textSecondary: isDark ? "#94A3B8" : "#475569"
    readonly property color textMuted: isDark ? "#64748B" : "#94A3B8"
    readonly property color textInverse: isDark ? "#0F172A" : "#FFFFFF"

    // Primary Brand Accent (Emerald Green / Institute Theme)
    readonly property color primary: isDark ? "#10B981" : "#059669"
    readonly property color primaryHover: isDark ? "#34D399" : "#047857"
    readonly property color primaryDark: isDark ? "#059669" : "#047857"
    readonly property color primarySoft: isDark ? "#0D2E26" : "#ECFDF5"
    readonly property color primaryText: isDark ? "#10B981" : "#065F46"

    // Secondary Accent (Corporate Blue)
    readonly property color accent: isDark ? "#3B82F6" : "#2563EB"
    readonly property color accentHover: isDark ? "#60A5FA" : "#1D4ED8"
    readonly property color accentSoft: isDark ? "#172554" : "#EFF6FF"

    // Semantic Status Colors
    readonly property color success: isDark ? "#10B981" : "#16A34A"
    readonly property color successSoft: isDark ? "#064E3B" : "#DCFCE7"
    readonly property color successText: isDark ? "#34D399" : "#15803D"

    readonly property color warning: isDark ? "#F59E0B" : "#D97706"
    readonly property color warningSoft: isDark ? "#451A03" : "#FEF3C7"
    readonly property color warningText: isDark ? "#FBBF24" : "#B45309"

    readonly property color danger: isDark ? "#EF4444" : "#DC2626"
    readonly property color dangerSoft: isDark ? "#450A0A" : "#FEE2E2"
    readonly property color dangerText: isDark ? "#F87171" : "#B91C1C"

    readonly property color info: isDark ? "#06B6D4" : "#0891B2"
    readonly property color infoSoft: isDark ? "#083344" : "#CFFAFE"
    readonly property color infoText: isDark ? "#22D3EE" : "#0E7490"

    // Sidebar & Navigation Specifics
    readonly property color sidebarBackground: isDark ? "#0D111A" : "#FFFFFF"
    readonly property color sidebarBorder: isDark ? "#1C2433" : "#E2E8F0"
    readonly property color sidebarActiveBackground: isDark ? "#162032" : "#EFF6FF"
    readonly property color sidebarActiveIndicator: isDark ? "#10B981" : "#059669"

    // TopBar
    readonly property color topBarBackground: isDark ? "#121824" : "#FFFFFF"
    readonly property color topBarBorder: isDark ? "#243048" : "#E2E8F0"

    // --- Spacing Tokens ---
    readonly property int spacingXXS: 2
    readonly property int spacingXS: 4
    readonly property int spacingSM: 8
    readonly property int spacingMD: 16
    readonly property int spacingLG: 24
    readonly property int spacingXL: 32
    readonly property int spacingXXL: 48

    // --- Corner Radius Tokens ---
    readonly property int radiusSM: 4
    readonly property int radiusMD: 8
    readonly property int radiusLG: 12
    readonly property int radiusXL: 16
    readonly property int radiusFull: 999

    // --- Typography Tokens ---
    readonly property string fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
    readonly property string fontMono: "Cascadia Code, Consolas, Courier New, monospace"

    readonly property int fontCaption: 11
    readonly property int fontSmall: 12
    readonly property int fontBody: 13
    readonly property int fontSubheading: 14
    readonly property int fontTitle: 16
    readonly property int fontHeader: 20
    readonly property int fontDisplay: 24

    readonly property int weightNormal: Font.Normal
    readonly property int weightMedium: Font.Medium
    readonly property int weightDemiBold: Font.DemiBold
    readonly property int weightBold: Font.Bold

    // --- Animation Durations ---
    readonly property int animFast: 150
    readonly property int animNormal: 250
    readonly property int animSlow: 350
}
