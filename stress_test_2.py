#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from threading import Thread
import os
import psutil
import signal
import subprocess
import time
import glob
import csv

class SystemInfoWindow(Gtk.Window):

    def __init__(self):

        info_text = "Set option"
        Gtk.Window.__init__(self, title="System info")
        self.set_default_size(1024, 768)
        self.set_border_width(1)
        
        self.box = Gtk.Box()
        self.add(self.box)
        
        self.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        adjustment = Gtk.Adjustment(0, 0, 42, 1, 10, 0)
        self.select_opt = Gtk.SpinButton()
        self.select_opt.set_adjustment(adjustment)
        
        get_info = Gtk.Button.new_with_label("Получить информацию")
        get_info.connect("clicked", self.call_dmidecode)

        options_list = Gtk.Label("0   BIOS\n"
                                 "1   System\n"
                                 "2   Baseboard\n"
                                 "3   Chassis\n"
                                 "4   Processor\n"
                                 "5   Memory Controller\n"
                                 "6   Memory Module\n"
                                 "7   Cache\n"
                                 "8   Port Connector\n"
                                 "9   System Slots\n"
                                 "10   On Board Devices\n"
                                 "11   OEM Strings\n"
                                 "12   System Configuration Options\n"
                                 "13   BIOS Language\n"
                                 "14   Group Associatins\n"
                                 "15   System Event Log\n"
                                 "16   Physical Memory Array\n"
                                 "17   Memory Device\n"
                                 "18   32-bit Memory Error\n"
                                 "19   Memory Array Mapped Address\n"
                                 "20   Memory Device Mapped Address\n"
                                 "21   Built-in Pointing Device\n"
                                 "22   Portable Battery\n"
                                 "23   System Reset\n"
                                 "24   Hardware Security\n"
                                 "25   System Power Controls\n"
                                 "26   Voltage Probe\n"
                                 "27   Cooling Device\n"
                                 "28   Temperature Probe\n"
                                 "29   Electrical Current Probe\n"
                                 "30   Out-of-band Remote Access\n"
                                 "31   Boot Integrity Services\n"
                                 "32   System Boot\n"
                                 "33   64-bit Memory Error\n"
                                 "34   Management Device\n"
                                 "35   Management Device Component\n"
                                 "36   Management Device Threshold Data\n"
                                 "37   Memory Channel\n"
                                 "38   IPMI Device\n"
                                 "39   Power Supply\n"
                                 "40   Additional Information\n"
                                 "41   Onboard Devices Extended Information\n"
                                 "42   Management Controller Host Interface")

        #Info View
        infowindow = Gtk.ScrolledWindow()
        infowindow.set_hexpand(True)
        infowindow.set_vexpand(True)

        self.sysinfo = Gtk.TextView()
        self.sysinfo.set_overwrite(False)
        self.sysinfo.set_editable(False)
        self.textbuffer_info = self.sysinfo.get_buffer()
        self.textbuffer_info.set_text(info_text)
        infowindow.add(self.sysinfo)
        
        self.vbox1.pack_start(self.select_opt, False, False, 0)
        self.vbox1.pack_start(get_info, False, False, 0)
        self.vbox1.pack_start(options_list, False, False, 0)
        self.vbox2.pack_start(infowindow, True, True, 0)
        self.box.pack_start(self.vbox1, False, True, 3)
        self.box.pack_start(self.vbox2, True, True, 0)
        
    def call_dmidecode(self, get_info):
        dmidecode_opt = self.select_opt.get_value_as_int()
        info = subprocess.Popen("dmidecode -t " + str(dmidecode_opt), stdout=subprocess.PIPE, shell = True)
        info_stdout,err = info.communicate()
        self.textbuffer_info.set_text(info_stdout.decode('utf-8'))

class ButtonWindow(Gtk.Window):
    def __init__(self):

        Gtk.Window.__init__(self, title="Утилита для мониторинга и тестирования")
        self.set_default_size(800, 600)
        self.box = Gtk.Box()

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_hexpand(True)
        scrolledwindow2.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_overwrite(False)
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("sensors_info")
        self.textview2 = Gtk.TextView()
        self.textview2.set_overwrite(False)
        self.textview2.set_editable(False)
        self.textbuffer2 = self.textview2.get_buffer()
        self.textbuffer2.set_text("cpu_freq and warnings")

        switch_gpu = Gtk.CheckButton("Тест видеокарты", use_underline=True)
        switch_gpu.connect("notify::active", self.switch_gpu_active)
        switch_cpu = Gtk.CheckButton("Тест ЦПУ", use_underline=True)
        switch_cpu.connect("notify::active", self.switch_cpu_active)
        switch_ram = Gtk.CheckButton("Тест памяти", use_underline=True)
        switch_ram.connect("notify::active", self.switch_ram_active)

        button_test = Gtk.ToggleButton("Запуск теста")
        button_test.connect("toggled", self.button_test_clicked, "1")
        button_sensors = Gtk.Button.new_with_label("Обнаружить датчики")
        button_sensors.connect("clicked", self.button_sensors_clicked)
        button_showinfo = Gtk.Button.new_with_label("Информация о системе")
        button_showinfo.connect("clicked", self.button_showinfo_clicked)
        
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        scrolledwindow.add(self.textview)
        scrolledwindow2.add(self.textview2)

        self.vbox_output = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox_output.pack_start(scrolledwindow, True, True, 3)
        self.vbox_output.pack_start(scrolledwindow2, True, True, 3)

        self.vbox_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox_buttons.pack_start(switch_gpu, False, False, 0)
        self.vbox_buttons.pack_start(switch_cpu, False, False, 0)
        self.vbox_buttons.pack_start(switch_ram, False, False, 0)
        self.vbox_buttons.pack_start(separator, False, False, 3)
        self.vbox_buttons.pack_start(button_test, False, False, 3)
        self.vbox_buttons.pack_start(button_sensors, False, False, 3)
        self.vbox_buttons.pack_start(button_showinfo, False, False, 3)

        self.add(self.box)
        self.box.pack_start(self.vbox_buttons, False, True, 3)
        self.box.pack_start(self.vbox_output, True, True, 3)

        self.update = Thread(target=self.monitoring)
        self.update.setDaemon(True)
        self.update.start()
#### End of init

    active1 = "off"
    active2 = "off"
    active3 = "off"
    gpu_pid = -2
    cpu_pid = -2
    mem_pid = -2
    test_start = 0

#### Check if test started
    def pid_check(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
        
#### Switches
    def switch_gpu_active(self, switch_gpu, gparam):
        if switch_gpu.get_active():
            self.active1 = "on"
        else:
            self.active1 = "off"
        
    def switch_cpu_active(self, switch_cpu, gparam):
        if switch_cpu.get_active():
            self.active2 = "on"
        else:
            self.active2 = "off"

    def switch_ram_active(self, switch_ram, gparam):
        if switch_ram.get_active():
            self.active3 = "on"
        else:
            self.active3 = "off"

#### Buttons
    def button_test_clicked(self, button_test, name):
        if button_test.get_active():
            if self.active1 == "on":
                gpu_test = subprocess.Popen("vblank_mode=0 glmark2-es2 --run-forever", shell = True, preexec_fn=os.setpgrp)
                self.gpu_pid = -gpu_test.pid
            if self.active2 == "on":
                cpu_test = subprocess.Popen("xterm -e stress-ng --cpu 0 --cpu-method all", shell = True, preexec_fn=os.setpgrp)
                self.cpu_pid = -cpu_test.pid
            if self.active3 == "on":
                mem_test = subprocess.Popen("xterm -e stress-ng --vm 2 --vm-bytes 1G", shell = True, preexec_fn=os.setpgrp)
                self.mem_pid = -mem_test.pid
            if self.active1 == "off" and self.active2 == "off" and self.active3 == "off":
                button_test.set_active(False)
            else:
                button_test.set_label("Остановить тест")
                self.test_start = 1

        else:
            if self.pid_check(self.gpu_pid):
                os.kill(self.gpu_pid, signal.SIGTERM)
            if self.pid_check(self.cpu_pid):
                os.kill(self.cpu_pid, signal.SIGTERM)
            if self.pid_check(self.mem_pid):
                os.kill(self.mem_pid, signal.SIGTERM)
            button_test.set_label("Запуск теста")
            self.test_start = 0

    def button_sensors_clicked(self, button_test):
        out_detect = subprocess.Popen("yes | sensors-detect", stdout=subprocess.PIPE, shell = True)
        detect_stdout,err = out_detect.communicate()
        self.textbuffer.set_text(detect_stdout.decode('utf-8'))

    def button_showinfo_clicked(self, button_showinfo):
        ChildWin = SystemInfoWindow()
        ChildWin.show_all()


### Finding CPU sensor
    ls_hwmon = os.listdir('/sys/class/hwmon/')
    if ls_hwmon != []:
        ls_hwmon_empty = 0
        for i in ls_hwmon:
            name_file = open('/sys/class/hwmon/' + i + '/name', 'r')
            sensor_name = name_file.read().rstrip()
            name_file.close()
            if sensor_name == 'coretemp':
                needed_sensor = '/sys/class/hwmon/' + i
        labels = sorted(glob.glob(needed_sensor + '/temp*_label'))
        sensor_data = sorted(glob.glob(needed_sensor + '/temp*_input'))
        core_count = len(labels)
        log_head = ['Время']
        for i in range(0, core_count):
            rlabel = open(labels[i], 'r').read().rstrip()
            log_head.append(rlabel + ", °C")
        log_head.extend(['Частота, ГГц', 'Загрузка, %'])
        logfile = open('/tmp/rdwa-monitoring.log', 'w')
        with logfile:
            writer = csv.writer(logfile, delimiter='\t')
            writer.writerow(log_head)
        logfile.close()
    else:
        ls_hwmon_empty = 1

#### Updating

    def monitoring(self):
        global min_freq
        global test_start
        min_freq = 500000000
        self.test_start = 0

        while True:
            if self.ls_hwmon_empty == 0:
                ls_hwmon_warning = 'Обнаружены датчики температуры ЦПУ в sysfs.\nПоказания записываются в /tmp/rdwa-monitoring.log'
                collected = [time.strftime("%H:%M:%S", time.gmtime())]
                for i in range(0, self.core_count):
                    rlabel = open(self.labels[i], 'r').read().rstrip()
                    rdata = str(int(open(self.sensor_data[i], 'r').read().rstrip())/1000)
                    collected.append(rdata)

                ###Writing log file
                logfile = open('/tmp/rdwa-monitoring.log', 'a')
                with logfile:
                    writer = csv.writer(logfile, delimiter='\t')
                    writer.writerow(collected)
            else:
                ls_hwmon_warning = 'Датчики темперануры ЦПУ не найдены.\nВозможно, ОС запущена в виртуальной машине'

            out_sensors = subprocess.Popen("sensors", stdout=subprocess.PIPE, shell = True)
            sensors_stdout,err = out_sensors.communicate()
            GObject.idle_add(
                self.textbuffer.set_text, 'Информация с датчиков системы:' + '\n\n' + sensors_stdout.decode('utf-8'),
                priority=GObject.PRIORITY_DEFAULT
                )
            
            if os.path.isfile("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"):
                scaling_cur_freq = open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r")
                curr_freq_raw = int(scaling_cur_freq.read())
                scaling_cur_freq.close()
                collected.append(str(curr_freq_raw/1000000))
                collected.append(str(psutil.cpu_percent()))

                if min_freq > curr_freq_raw:
                    min_freq = curr_freq_raw

                if self.test_start == 1 and curr_freq_raw <= min_freq:
                    trottling = "СИСТЕМА ОХЛАЖДЕНИЯ: НЕИСПРАВНОСТЬ!!!"
                else:
                    trottling = "СИСТЕМА ОХЛАЖДЕНИЯ: OK"

                curr_freq = "Текущая частота ЦПУ (GHz): " + str(curr_freq_raw/1000000) + "\n" + trottling + "\n" + ls_hwmon_warning
                curr_load = "Текущая нагрузка на ЦПУ (%): " + collected[-1]
                GObject.idle_add(
                    self.textbuffer2.set_text, curr_load + "\n" + curr_freq,
                    priority=GObject.PRIORITY_DEFAULT
                    )
            else:
                GObject.idle_add(
                    self.textbuffer2.set_text, "Не удалось обнаружить данные о частоте ЦПУ.\nВозможно, ОС запущена в виртуальной машине",
                    priority=GObject.PRIORITY_DEFAULT
                    )

            time.sleep(1)

win = ButtonWindow()
GObject.threads_init()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
