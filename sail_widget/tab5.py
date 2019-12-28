import os

from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *

from sail_widget.s_label import SLabel
from sail_widget.s_button import HelpButton, SButton
from sail_widget.tooltip import create_tooltip
from sail_widget.s_entry import SEntry
from sail_widget.s_toplevel import SMultiTopLevel

from tools.read_scores import read_scores, read_folder_scores, read_root_folder_scores
from tools.receptor_processor import gen_config, proteins2dir
from tools.text import *
from tools.configer import Configer
from tools.check import Check
from tools.file_processor import create_scores_file, extract_file


# 工具
class Tab5(object):

    def __init__(self, tab, config):
        self.root = tab
        self.config = config

        # 需要保存的参数
        self.choose_ligand_entry = None
        self.choose_receptor_entry = None
        self.choose_pdbqt_dir_entry = None
        self.choose_scores_entry = None
        self.choose_output_entry = None
        self.choose_extract_folder_entry = None

        # 创建窗体
        self.create_all_config()
        self.create_move_pdbqt()
        self.create_extract_scores()
        self.extract_from_file()

        # 帮助按钮
        help_button = HelpButton(root=self.root, help_text=TAB5_HELP_TEXT, x=410, y=300, width=80)
        create_tooltip(help_button.help_button, "获取帮助")

    def create_all_config(self):
        all_config_labelframe = LabelFrame(self.root, text="受体全局对接")
        all_config_labelframe.place(x=10, y=10, width=570, height=85)

        choose_ligand = SButton(all_config_labelframe, text="选择配体", x=10, y=0)
        create_tooltip(choose_ligand.button, "选择参考配体pdbqt文件")
        self.choose_ligand_entry = SEntry(all_config_labelframe, textvariable=StringVar(),
                                          text=Configer.get_para("refer_ligand"),
                                          x=100, y=3, width=450)
        create_tooltip(self.choose_ligand_entry.entry, "选择的参考配体")
        choose_ligand.bind_open_file(self.choose_ligand_entry.textvariable,
                                     title="选择配体pdbqt文件",
                                     file_type="pdbqt")

        choose_receptor = SButton(all_config_labelframe, text="选择受体", x=10, y=30)
        create_tooltip(choose_receptor.button, "选择需要全局搜索的单/多个受体文件夹，具体请看帮助或者教程")
        self.choose_receptor_entry = SEntry(all_config_labelframe, textvariable=StringVar(),
                                            text=Configer.get_para("refer_receptor"),
                                            x=100, y=33, width=350)
        create_tooltip(self.choose_receptor_entry.entry, "选择的参考")
        choose_receptor.bind_open_dir(entry_text=self.choose_receptor_entry.textvariable,
                                      title="选择单/多个受体所在文件夹")
        generate_button = SButton(all_config_labelframe, text="生成文件", x=460, y=30, width=90)
        create_tooltip(generate_button.button, "生成全局对接的多个config文件")
        generate_button.button.bind("<Button-1>", self.generate_configs)

    def create_move_pdbqt(self):
        move_pdbqt_labelframe = Labelframe(self.root, text="移动受体文件")
        move_pdbqt_labelframe.place(x=10, y=100, width=570, height=50)

        choose_pdbqt_dir = SButton(move_pdbqt_labelframe, text="选择文件", x=10, y=0)
        create_tooltip(choose_pdbqt_dir.button, "选择包含pdbqt受体的文件夹")
        self.choose_pdbqt_dir_entry = SEntry(move_pdbqt_labelframe, textvariable=StringVar(),
                                             text=Configer.get_para("pdbqt_dir"),
                                             x=100, y=3, width=350)
        create_tooltip(self.choose_pdbqt_dir_entry.entry, "选择包含pdbqt受体的文件夹")
        choose_pdbqt_dir.bind_open_dir(self.choose_pdbqt_dir_entry.textvariable,
                                       title="选择有pdbqt受体的文件夹")
        move_button = SButton(move_pdbqt_labelframe, text="移动文件", x=460, y=0, width=90)
        create_tooltip(move_button.button, "开始移动pdbqt文件并重命名为preped.pdbqt")
        move_button.button.bind("<Button-1>", self.move_file)

    def create_extract_scores(self):
        extract_scores_labelframe = Labelframe(self.root, text="提取分数")
        extract_scores_labelframe.place(x=10, y=155, width=570, height=50)

        choose_score = SButton(root=extract_scores_labelframe, text="选择单个文件", x=10, y=0)
        create_tooltip(choose_score.button, "选择单个打分结果pdbqt文件")
        choose_scores_dir = SButton(root=extract_scores_labelframe, text="选择文件夹", x=100, y=0)
        create_tooltip(choose_scores_dir.button, "选择多个打分结果所在的文件夹")
        self.choose_scores_entry = SEntry(root=extract_scores_labelframe, textvariable=StringVar(),
                                          text=Configer.get_para("choose_score_file"),
                                          x=190, y=4, width=260)
        create_tooltip(self.choose_scores_entry.entry, "选择的文件/文件夹")
        choose_score.bind_open_file(self.choose_scores_entry.textvariable,
                                    title="选择对接结果pdbqt文件",
                                    file_type="pdbqt")
        choose_scores_dir.bind_open_dir(self.choose_scores_entry.textvariable,
                                        title="选择含有对接结果的文件夹")
        extract_button = SButton(extract_scores_labelframe, text="提取分数", x=460, y=0, width=90)
        create_tooltip(extract_button.button, "提取分数结果。如果是单个文件直接显示窗口。"
                                              "如果选择文件夹，则输出txt文件到选择的文件夹")
        extract_button.button.bind("<Button-1>", self.extract_score)

    def extract_from_file(self):
        extract_from_file_labelframe = Labelframe(self.root, text="从文件提取配体")
        extract_from_file_labelframe.place(x=10, y=210, width=570, height=85)

        choose_file_button = SButton(extract_from_file_labelframe,
                                     text="选择输入文件",
                                     x=10, y=0)
        create_tooltip(choose_file_button.button, "选择输入的txt文件")
        self.choose_output_entry = SEntry(extract_from_file_labelframe, textvariable=StringVar(),
                                          text=Configer.get_para("output_txt"),
                                          x=100, y=3, width=450)
        create_tooltip(self.choose_output_entry.entry, "选择的txt文件")
        choose_file_button.bind_open_file(entry_text=self.choose_output_entry.textvariable,
                                          title="选择输入的txt文件",
                                          file_type="txt")

        choose_output_button = SButton(extract_from_file_labelframe,
                                       text="选择提取目录",
                                       x=10, y=33)
        create_tooltip(choose_output_button.button, "选择提取输出的目录")
        self.choose_extract_folder_entry = SEntry(extract_from_file_labelframe, textvariable=StringVar(),
                                                  text=Configer.get_para("extract_folder"),
                                                  x=100, y=33, width=350)
        create_tooltip(self.choose_extract_folder_entry.entry, "选择提取输出的目录")
        choose_output_button.bind_open_dir(entry_text=self.choose_extract_folder_entry.textvariable,
                                           title="选择输出目录")
        extract_button = SButton(extract_from_file_labelframe, text="提取配体", x=460, y=30, width=90)
        create_tooltip(extract_button.button, "根据输入的文件提取配体")
        extract_button.button.bind("<Button-1>", self.extract_file)

    def generate_configs(self, event):
        ligand = self.choose_ligand_entry.textvariable.get()
        proteins_dir = self.choose_receptor_entry.textvariable.get()

        if Check.check_path(ligand) or Check.check_path(proteins_dir):
            messagebox.showerror("错误", "路径不能空或者包含空格！")
            return

        if not ligand.endswith(".pdbqt"):
            messagebox.showerror("错误", "受体必须是pdbqt格式")
            return

        receptors_dir = []

        # 如果是一个受体文件夹
        if os.path.exists(proteins_dir + os.sep + "preped.pdbqt"):
            receptors_dir.append(proteins_dir + os.sep + "preped.pdbqt")
        else:
            for receptor in os.listdir(proteins_dir):
                pdbqt_file = proteins_dir + os.sep + receptor + os.sep + "preped.pdbqt"
                if os.path.exists(pdbqt_file):
                    receptors_dir.append(pdbqt_file)
                else:
                    print("%s中没有preped.pdbqt文件" % receptor)

        if len(receptors_dir) == 0:
            messagebox.showerror("错误", "没有检测到受体文件！")
            return

        for receptor_dir in receptors_dir:
            gen_config(receptor_dir, ligand)
            print("------------------------------------------------------------")
            print("%s准备成功！" % receptor_dir)
            print("------------------------------------------------------------")

        messagebox.showinfo("成功", "已经生成多个配置文件！")

    def move_file(self, event):
        proteins_dir = self.choose_pdbqt_dir_entry.textvariable.get()

        if Check.check_path(proteins_dir):
            messagebox.showerror("路径不为空，不能包括空格！")
            return

        if not os.path.exists(proteins_dir):
            messagebox.showerror("错误", "选择文件夹不存在")
            return

        proteins2dir(proteins_dir)
        messagebox.showinfo("成功", "文件成功移动！")

    def extract_score(self, event):
        score_file = self.choose_scores_entry.textvariable.get()

        if Check.check_path(score_file):
            messagebox.showerror("错误", "路径不能为空或者包含空格！")
            return

        # 如果是单个pdbqt文件，弹出窗口直接显示结果。
        if score_file.endswith(".pdbqt"):

            scores = read_scores(score_file)

            if len(scores) == 0:
                messagebox.showerror("错误", "选择的文件中没有检测到分数！")
                return

            file_name = os.path.split(score_file)[-1][0:-6]
            score_top = SMultiTopLevel(self.root, 600, 100, file_name).toplevel
            SLabel(score_top, text="当前文件:" + file_name, x=10, y=0)

            SLabel(score_top, text="number", x=10, y=30)
            SLabel(score_top, text="scores", x=10, y=60)
            i = 0
            while i < len(scores):
                SLabel(score_top, text=str(i + 1), x=80 + (50 * i), y=30)
                SLabel(score_top, text=scores[i], x=80 + (50 * i), y=60)
                i += 1

        # 如果是文件夹，在该文件夹中生成分数文件
        elif os.path.isdir(score_file):
            output_file = score_file + os.sep + "scores.txt"
            # 如果是子目录，没有受体，只输出分数最高的
            if os.listdir(score_file)[0].endswith(".pdbqt"):
                scores = read_folder_scores(score_file, mode=1)
                create_scores_file(output_file, scores, mode=1)
            else:
                scores = read_root_folder_scores(score_file, mode=1)
                create_scores_file(output_file, scores, mode=0)
            messagebox.showinfo("保存成功！", "保存分数文件到%s" % output_file)
        else:
            messagebox.showerror("输入错误", "请选择pdbqt文件或者选择文件夹！")
            return

    def extract_file(self, event):
        output_file = self.choose_output_entry.textvariable.get()
        extract_path = self.choose_extract_folder_entry.textvariable.get()

        if Check.check_path(output_file) or Check.check_path(extract_path):
            messagebox.showerror("错误", "路径不能有空或者有空格")
            return

        if not output_file.endswith(".txt"):
            messagebox.showerror("错误", "输入必须为txt文件!")
            return

        if not extract_file(output_file, extract_path):
            messagebox.showerror("错误!", "输入文件内容无法识别！"
                                        "具体参见命令行。")
            return
        messagebox.showinfo("成功", "成功提取配体！")

    def save_para(self):
        self.config.para_dict["refer_ligand"] = self.choose_ligand_entry.textvariable.get()
        self.config.para_dict["refer_receptor"] = self.choose_receptor_entry.textvariable.get()
        self.config.para_dict["pdbqt_dir"] = self.choose_pdbqt_dir_entry.textvariable.get()
        self.config.para_dict["choose_score_file"] = self.choose_scores_entry.textvariable.get()
        self.config.para_dict["output_txt"] = self.choose_output_entry.textvariable.get()
        self.config.para_dict["extract_folder"] = self.choose_extract_folder_entry.textvariable.get()
