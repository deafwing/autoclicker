import PySimpleGUI as sg
import pyautogui
import threading
import keyboard
import time

# Global control for the clicking thread
clicking_active = False
stop_event = threading.Event()

def clicker_thread(settings):
    """Background thread that handles the actual clicking logic."""
    global clicking_active
    
    # Calculate total interval in seconds
    try:
        interval = (int(settings['-HR-']) * 3600) + \
                   (int(settings['-MIN-']) * 60) + \
                   float(settings['-SEC-'])
    except ValueError:
        interval = 1.0  # Fallback to 1s if input is invalid

    count = 0
    max_repeat = settings['-REPEATCNT-'] if settings['-REPEAT-'] else float('inf')
    
    while not stop_event.is_set():
        # Handle Cursor Position
        if settings['-PICKLOCATION-']:
            pyautogui.click(x=int(settings['-X-']), y=int(settings['-Y-']), 
                            button=settings['-WHICHBUTTON-'].lower(), 
                            clicks=2 if settings['-CLICKTYPE-'] == 'Double' else 1)
        else:
            pyautogui.click(button=settings['-WHICHBUTTON-'].lower(), 
                            clicks=2 if settings['-CLICKTYPE-'] == 'Double' else 1)
        
        count += 1
        if count >= max_repeat:
            break
            
        time.sleep(interval)

    clicking_active = False

def setup_layout():
    # Tab 1: Interval
    tab1_layout = [[sg.Input('0', size=(5,1), key='-HR-'), sg.Text('hours', expand_x=True), 
                   sg.Input('0', size=(5,1), key='-MIN-'), sg.Text('mins', expand_x=True), 
                   sg.Input('0', size=(5,1), key='-SEC-'), sg.Text('Sec', expand_x=True)]]

    # Tab 2: Options
    tab2_layout = [[sg.Text('Mouse button: '), 
                   sg.Combo(['Left', 'Middle', 'Right'], default_value='Left', key='-WHICHBUTTON-')],
                   [sg.Text('Click type: '), 
                    sg.Combo(['Single', 'Double'], default_value='Single', key='-CLICKTYPE-')]]

    # Tab 3: Repeat
    tab3_layout = [[sg.Radio('Repeat', key='-REPEAT-', default=True, group_id=1), 
                   sg.Spin(initial_value=1, size=(3,1), values=list(range(1,101)), key='-REPEATCNT-')], 
                   [sg.Radio('Repeat until stopped', group_id=1, key='-REPEATUNTILSTOPPED-')]]

    # Tab 4: Position
    tab4_layout = [[sg.Radio('Current location', key='-CURRENTLOCATION-', default=True, group_id=2), 
                   sg.Radio('Pick location', key='-PICKLOCATION-', group_id=2),
                    sg.Text('X'), sg.Input('0', size=(4,1), key='-X-'), sg.Text('Y'), sg.Input('0', size=(4,1), key='-Y-')]]

    layout = [
        [sg.TabGroup([[sg.Tab('Click Interval', tab1_layout), 
                      sg.Tab('Click Options', tab2_layout), 
                      sg.Tab('Click Repeat', tab3_layout), 
                      sg.Tab('Cursor position', tab4_layout)]], expand_x=True)],
        [sg.Button('Start (F6)', expand_x=True, key='-START-'), 
         sg.Button('Stop (F6)', expand_x=True, key='-STOP-')],
        [sg.Text("Global Hotkey: F6", justification='center', expand_x=True)]
    ]
    return sg.Window("HGL's Auto Clicker", layout, finalize=True)

# Global hotkey handler
def toggle_clicking(window):
    global clicking_active
    if not clicking_active:
        window.write_event_value('-START-', None)
    else:
        window.write_event_value('-STOP-', None)

# Main Logic
window = setup_layout()
keyboard.add_hotkey('f6', lambda: toggle_clicking(window))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    
    if event == '-START-':
        if not clicking_active:
            clicking_active = True
            stop_event.clear()
            threading.Thread(target=clicker_thread, args=(values,), daemon=True).start()
            window['-START-'].update(disabled=True)
            window['-STOP-'].update(disabled=False)

    if event == '-STOP-':
        clicking_active = False
        stop_event.set()
        window['-START-'].update(disabled=False)
        window['-STOP-'].update(disabled=True)

window.close()
