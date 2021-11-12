import pywinauto
from pywinauto.application import Application
from glob import glob
import pandas as pd
import numpy as np
from datetime import datetime
import psutil
import os
import re


class PiCurrentAnalyzer(object):
    def __init__(self, executable_path):
        self.executable_path = executable_path
        self.save_dir_path = "logs/output"
        self.preprocessed_save_dir_path = "logs/processed"
        self.app = None
        self.dialog = None
        self.first_run = True

        if not os.path.isdir(self.save_dir_path):
            os.makedirs(self.save_dir_path, exist_ok=True)
        if not os.path.isdir(self.preprocessed_save_dir_path):
            os.makedirs(self.preprocessed_save_dir_path, exist_ok=True)

    def open(self):
        self.close()

        try:
            self.app = Application(backend='win32', allow_magic_lookup=False).start(self.executable_path)
        except UserWarning:
            pass
        self.dialog = self.app['ChargerLAB POWER-Z Standard Edition']
        self.dialog.wait('visible')

    def set_title(self, title=None):
        if title is None or title == '':
            return
            
        self.dialog['App Setting'].click()
        setting_dialog = self.app['Setting']
        setting_dialog['Edit0'].click()  # Notify window change of test
        setting_dialog['Edit0'].set_edit_text(self.save_dir_path)
        setting_dialog['Edit2'].click()
        setting_dialog['Edit2'].set_edit_text(title)
        setting_dialog['Edit0'].type_keys('{ENTER}')

    def close(self):
        if self.dialog is not None:
            try:
                self.dialog.close()
            except:
                print("Error closing dialog")
            self.dialog = None
        if self.app is not None:
            try:
                self.app.close()
            except:
                print("Error closing app")
            self.app = None
            
        self.first_run = True

        # Kill previous running application
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == re.split(r'\\|/', self.executable_path).pop():
                print("Killing previous running analyzer %d ..." % proc.pid)
                proc.kill()

    def begin(self, title=None):
        self.set_title(title)
        self.dialog["High refresh rate"].check()

        if self.first_run:
            btn_text = 'Run Pause'
        else:
            btn_text = '开始记录'
        self.first_run = False

        try:
            # Start current(A) monitoring
            self.dialog[btn_text].click()
            return True
        except pywinauto.findbestmatch.MatchError:
            pass
        return False

    def end(self, title=None):
        try:
            # Stop current(A) monitoring
            self.dialog['Stop'].click()

            # Set csvout as output filename
            self.set_title(title)

            # Save csv file
            self.dialog['導出數據 *.csv'].click()
            child_dialog = self.app['Power-Z']
            child_dialog['확인'].click()
        except pywinauto.findbestmatch.MatchError:
            pass

        if self.dialog is not None:
            self.dialog.close()
            
    def postprocess(self, model_name, elapsed_time_sec, total_frames):
        # 출력된 csv 파일에 대한 후처리를 진행하고
        # 파일을 이동한다.
        csv_list = glob(os.path.join(self.save_dir_path, "*.csv"))
        metricies = []

        for i, filename in enumerate(csv_list):
            # 파일을 먼저 읽고 처리한다.
            # Ensure there's no non-latin character in file!
            data = pd.read_csv(filename, encoding='latin1', skiprows=[0]).rename(columns={
                'Vbus(V)': 'vbus',
                'Ibus(A)': 'ibus',
                'Power(W)': 'power',
                'Vd+(V)': 'vdp',
                'Vd-(V)': 'vdm',
                'energy(Wh)': 'wh',
                'temperature(¡É)': 'temp'
            }).interpolate()

            # watts = data['vbus'] * data['power']
            # watts = watts.to_numpy()
            energy_consumption = data['wh'].to_numpy()[-1]

            save_filename = os.path.join(self.preprocessed_save_dir_path, '%s-%s-frame%dms-total%dsec-%02d.csv') % (
                datetime.now().strftime("%Y%m%d"), model_name,
                elapsed_time_sec / total_frames * 1000, elapsed_time_sec, i)

            # print("Moving %s -> %s" % (filename, save_filename))
            data.to_csv(save_filename, index=False)
            os.remove(filename)
            # os.rename(filename, save_filename)

            metricies.append(energy_consumption)

        total_energy_consumption_mwh = int(np.array(metricies).sum() * 1000)
        # print("Power Metric: %d mWh" % total_energy_consumption_mwh)

        return total_energy_consumption_mwh