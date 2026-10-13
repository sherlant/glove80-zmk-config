#Requires AutoHotkey v2.0
#SingleInstance Force
; Software KVM, Windows side. F13/F14 are sent by the Glove80 kvm_pc2/kvm_pc1
; macros (HYPR+F2 / HYPR+F1) right before the keyboard switches BT profile.
; Needs ControlMyMonitor.exe (NirSoft) and mouse-host.py next to this script.

CMM := A_ScriptDir "\ControlMyMonitor.exe"
MONITOR := "32P625Q"   ; check with: ControlMyMonitor.exe /smonitors monitors.txt

; HYPR+F1: hand screen + mouse over to the Linux PC (DisplayPort-1, host 1)
F14:: {
    Run '"' CMM '" /SetValue "' MONITOR '" 60 15', , "Hide"
    Run 'pythonw "' A_ScriptDir '\mouse-host.py" 1', , "Hide"
}

; HYPR+F2 while already here: take the screen back (HDMI-1)
F13:: {
    Run '"' CMM '" /SetValue "' MONITOR '" 60 17', , "Hide"
}
