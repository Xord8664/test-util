#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import subprocess

class YesNoDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Confirm", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label("Runned services will be stopped, stopped services will be ran.\nAre you sure?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class Error(Gtk.Dialog):    
    def __init__(self, parent):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "This is an ERROR MessageDialog")
        dialog.format_secondary_text(
            "And this is the secondary text that explains things.")
        dialog.run()
        print("ERROR dialog closed")

class AdminWindow(Gtk.Window):
    path_number = 0
    def __init__(self):
        Gtk.Window.__init__(self, title="AdminTool")
        self.set_default_size(1024, 768)

#### Get services list
        self.liststore = Gtk.ListStore(str, str, str, str, bool, int)
        cmd = "systemctl list-units --type socket,service -a | sed 's/● //' | awk '{print $1,$2,$3,$4}' | tail -n+2 | head -n-7"
        units = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out,err = units.communicate()
        srvcs = out.decode('utf-8').splitlines()
        d = {}
        for i in srvcs: d.update({i.split(" ")[0]:[i.split(" ")[1], i.split(" ")[2], i.split(" ")[3]]})
        
        for k in d:
            self.liststore.append([k, d[k][0], d[k][1], d[k][2], False, self.path_number])
            self.path_number +=1

#### Create table
        table = Gtk.TreeView(model=self.liststore)
        render_text = Gtk.CellRendererText()
        
        column_text = Gtk.TreeViewColumn("Service", render_text, text=0)
        table.append_column(column_text)
        
        column_text_load = Gtk.TreeViewColumn("LOAD", render_text, text=1)
        table.append_column(column_text_load)
        
        column_text_active = Gtk.TreeViewColumn("Active", render_text, text=2)
        table.append_column(column_text_active)
        
        column_text_state = Gtk.TreeViewColumn("State", render_text, text=3)
        table.append_column(column_text_state)
        
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        
        column_toggle = Gtk.TreeViewColumn("Toggle", renderer_toggle, active=4)
        table.append_column(column_toggle)
        
#### Buttons
        startstop_button = Gtk.Button.new_with_label("change state")
        startstop_button.connect("clicked", self.change_state)
        
#### Packing

        self.box = Gtk.Box()
        self.add(self.box)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        services_window = Gtk.ScrolledWindow()
        services_window.set_hexpand(True)
        services_window.set_vexpand(True)
        
        services_window.add(table)
        services_box.pack_start(services_window, True, True, 0)
        
        button_box.pack_start(startstop_button, False, False, 0)
        
        self.box.pack_start(button_box, False, True, 3)
        self.box.pack_start(services_box, True, True, 3)
        
        # ~ print(path_number)
        
    services = {}
    
    def on_cell_toggled(self, widget, path):
        self.liststore[path][4] = not self.liststore[path][4]
        if self.liststore[path][4] == False:
            del self.services[self.liststore[path][0]]
        else:
            self.services.update({self.liststore[path][0] : [ self.liststore[path][3], self.liststore[path][4] ]})
        
    def change_state(self, startstop_button):
        dialog = YesNoDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for s in self.services:
                for r in range(0, self.path_number):
                    if s == self.liststore[r][0]:
                        print("Doing something with " + s)
                        command = subprocess.Popen("systemctl show -p SubState --value " + s, shell=True, stdout=subprocess.PIPE)
                        result,err = command.communicate()
                        if err != None:
                            err_decoded = err.decode('utf-8').rstrip()
                        
                        decoded_result = result.decode('utf-8').rstrip()
                        print(decoded_result)
                        self.liststore[r][4] = False
                        self.liststore[r][3] = decoded_result
        else:
            print("Canceled")
        dialog.destroy()

        

win = AdminWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
