#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import subprocess
import sys
import paramiko

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

class AdminWindow(Gtk.Window):
    path_number = 0     # Row number in list store
    hosts = {}      # List store data (all data about all hosts)
    services = {}       # Хуй знает, на всякий случай
    
    cmd = "systemctl list-units --type socket,service -a | sed 's/● //' | awk '{print $1,$2,$3,$4}' | tail -n+2 | head -n-7"
    
    # gonna be used for tabs creation
    host = 'localhost'
    port = 'port'
    user = 'user'
    passwd = 'pass'
    
    def __init__(self):
        Gtk.Window.__init__(self, title="AdminTool")
        self.set_default_size(1024, 768)
        
#### Services on localhost

        units = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
        out,err = units.communicate()
        local_services = out.decode('utf-8').splitlines()
        
        local_services_dict = {}
        for i in local_services:
            local_services_dict.update({i.split(" ")[0]:[i.split(" ")[1], i.split(" ")[2], i.split(" ")[3], False, self.path_number]})       # False for checkbox in list store
            self.path_number += 1
        self.path_number = 0
####
        self.hosts.update({ self.host: [ self.port, self.user, self.passwd, local_services_dict ] })
        
        self.liststore = Gtk.ListStore(str, str, str, str, bool, int)
        for k in self.hosts['localhost'][3]:
            self.liststore.append([k, self.hosts['localhost'][3][k][0], self.hosts['localhost'][3][k][1], self.hosts['localhost'][3][k][2], self.hosts['localhost'][3][k][3], self.hosts['localhost'][3][k][4]])

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
        
#### Buttons and entries
        startstop_button = Gtk.Button.new_with_label("change state")
        startstop_button.connect("clicked", self.change_state)
        
        connect_button = Gtk.Button.new_with_label("connect")
        connect_button.connect("clicked", self.connect_func)
        
        self.entry_host = Gtk.Entry()
        self.entry_port = Gtk.Entry()
        self.entry_user = Gtk.Entry()
        self.entry_passwd = Gtk.Entry()

        self.entry_host.set_text(self.host)
        self.entry_port.set_text(self.port)
        self.entry_user.set_text(self.user)
        self.entry_passwd.set_text(self.passwd)
        self.entry_passwd.set_visibility(False)
        
        label_remote = Gtk.Label("Connect to remote PC:")
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)


#### Packing
        connect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        connect_box.pack_start(separator, False, False, 6)
        connect_box.pack_start(label_remote, False, False, 3)
        connect_box.pack_start(self.entry_host, False, False, 3)
        connect_box.pack_start(self.entry_port, False, False, 3)
        connect_box.pack_start(self.entry_user, False, False, 3)
        connect_box.pack_start(self.entry_passwd, False, False, 3)
        connect_box.pack_start(connect_button, False, False, 3)

        self.box = Gtk.Box()
        self.add(self.box)
        
        self.notebook = Gtk.Notebook()
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        services_window = Gtk.ScrolledWindow()
        services_window.set_hexpand(True)
        services_window.set_vexpand(True)
        
        services_window.add(table)
        services_box.pack_start(services_window, True, True, 0)
        self.notebook.append_page(services_box, Gtk.Label('localhost'))
        
        button_box.pack_start(startstop_button, False, False, 3)
        button_box.pack_start(connect_box, False, False, 0)
        
        self.box.pack_start(button_box, False, True, 0)
        self.box.pack_start(self.notebook, True, True, 3)
    
    
    
    def on_cell_toggled(self, widget, path):
        self.liststore[path][4] = not self.liststore[path][4]
        if self.liststore[path][4] == False:
            del self.services[self.liststore[path][0]]
        else:
            self.services.update({self.liststore[path][0] : [ self.liststore[path][3], self.liststore[path][4] ]})
            
    def change_state(self, startstop_button):
        print(self.notebook.get_tab_label_text(self.notebook.get_nth_page(self.notebook.get_current_page())))
        # ~ if self.notebook.get_tab_label_text(self.notebook.get_nth_page(self.notebook.get_current_page())) == 'localhost':
            # ~ print(True)
            # ~ dialog = YesNoDialog(self)
            # ~ response = dialog.run()
            # ~ if response == Gtk.ResponseType.OK:
                # ~ for s in self.hosts['localhost'][3]:
                    # ~ if self.hosts['localhost'][3][s][4] == self.liststore[s][0]:
                        # ~ print("Doing something with " + s)
                        # ~ command = subprocess.Popen("systemctl show -p SubState --value " + s, shell=True, stdout=subprocess.PIPE)
                        # ~ result,err = command.communicate()
                        # ~ if err != None:
                            # ~ err_decoded = err.decode('utf-8').rstrip()
                        # ~ decoded_result = result.decode('utf-8').rstrip()
                        # ~ print(decoded_result)
                        # ~ self.liststore[r][4] = False
                        # ~ self.liststore[r][3] = decoded_result
                # ~ dialog.destroy()
            # ~ else:
                # ~ dialog.destroy()

    def connect_func(self, connect_button):
        self.host = self.entry_host.get_text()
        self.port = self.entry_port.get_text()
        self.user = self.entry_user.get_text()
        self.passwd = self.entry_passwd.get_text()
        self.hosts.update({ self.host: [ self.port, self.user, self.passwd, self.services ] })
        new_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        new_label = Gtk.Label(self.host)
        new_box.pack_start(new_label, False, False, 3)
        self.notebook.append_page(new_box, Gtk.Label(self.host))
        self.notebook.show_all()
        self.ssh_connect()
        
    def ssh_connect(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(self.host, port=int(self.port), username=self.user, password=self.passwd)

        stdin, stdout, stderr = client.exec_command(self.cmd)
        
        services = stdout.read().decode('utf-8').rstrip().splitlines()
        remote_services = {}
        service_number = 0
        for i in services:
            i = i.split(" ")
            remote_services.update({ i[0]: [i[1], i[2], i[3], False, service_number]})
            service_number += 1
            
        self.hosts.update({ self.host: [ self.port, self.user, self.passwd, remote_services ] })
        client.close()
        
        
    def get_services(self):
        cmd = "systemctl list-units --type socket,service -a | sed 's/● //' | awk '{print $1,$2,$3,$4}' | tail -n+2 | head -n-7"
        units = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out,err = units.communicate()
        local_services = out.decode('utf-8').splitlines()

win = AdminWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
