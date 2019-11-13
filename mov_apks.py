# coding:utf-8
import os
import pandas as pd
import threadpool
import shutil


APK_PATH = "/mnt/fit-Knowledgezoo-vault/vault/apks"
CSV_FOLDER = "/home/tianming/yanjie/analyzecsv/year_folder"
MOV_PATH = "/home/tianming/yanjie/year_data"
Year_record = "year_record.txt"


def getFileList(rootDir, pickstr):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


class Analysis:
    def __init__(self):
        self.max_jobs = 15

    def process_one(self, args):
        file = args
        flag = 1
        try:
            df = pd.read_csv(file, header=0)
            line_num = len(df)
            if line_num < 7:
                return
            pkg = os.path.split(file)[-1][:-4]
            pkg_name = os.path.join(MOV_PATH, pkg)
            if not os.path.exists(pkg_name):
                os.mkdir(pkg_name)

            for i in range(line_num):
                SHA256 = df.iloc[i]['sha256']
                if not os.path.exists(os.path.join(APK_PATH, SHA256 + ".apk")):
                    print(SHA256 + " not exists!")
                    flag = 0
                    continue
                apk_path = os.path.join(APK_PATH, SHA256 + ".apk")
                new_path = os.path.join(MOV_PATH, os.path.join(pkg_name, SHA256 + ".apk"))
                cmd = "cp " + apk_path + " " + new_path
                #child = pexpect.spawn(cmd)
                #child.wait()
                os.system(cmd)
                print(SHA256 + " moved!")
            if flag == 1:
                with open(Year_record, "a+") as f:
                    f.write(pkg + " " + str(line_num) + "\n")
            else:
                shutil.rmtree(pkg_name)

        except Exception as e:
            print(e, file)
            return None

    def process(self):
        files = getFileList(CSV_FOLDER, ".csv")
        args = [file for file in files]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process()

if __name__ == '__main__':
    if os.path.exists(Year_record):
        os.remove(Year_record)
    if not os.path.exists(MOV_PATH):
        os.mkdir(MOV_PATH)
    analysis = Analysis()
    analysis.start()
