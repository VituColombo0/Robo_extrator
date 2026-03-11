import re
import os

filepath = r'c:\Users\Vitu\Desktop\Robo_Extrator_Final\scripts\robo_extrator_final.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Tkinter imports at the top
imports = '''
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
'''
code = code.replace('import numpy as np', imports + '\nimport numpy as np')

# 2. Add GUI Log support
log_funcs_old = '''
def _log(msg):
    linha = f"[INFO] {msg}"
    print(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass

def _warn(msg):
    linha = f"[WARN] {msg}"
    print(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass

def _error(msg):
    linha = f"[ERROR] {msg}"
    print(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass
'''

log_funcs_new = '''
GUI_LOG_CALLBACK = None

def _escrever_gui(msg):
    if GUI_LOG_CALLBACK:
        try:
            GUI_LOG_CALLBACK(msg)
        except:
            pass

def _log(msg):
    linha = f"[INFO] {msg}"
    print(linha)
    _escrever_gui(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass

def _warn(msg):
    linha = f"[WARN] {msg}"
    print(linha)
    _escrever_gui(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass

def _error(msg):
    linha = f"[ERROR] {msg}"
    print(linha)
    _escrever_gui(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\\n")
        except:
            pass
'''
code = code.replace(log_funcs_old.strip(), log_funcs_new.strip())

# 3. Update _esperar_download_csv
esperar_old = '''
def _esperar_download_csv(pasta, timeout_s=150):
    t0 = time.time()
    ignore_ext = (".crdownload", ".part", ".tmp")

    while time.time() - t0 < timeout_s:
        files = [os.path.join(pasta, f) for f in os.listdir(pasta)]
        files = [f for f in files if os.path.isfile(f)]

        if any(f.lower().endswith(ignore_ext) for f in files):
            time.sleep(0.5)
            continue

        csvs = [f for f in files if f.lower().endswith(".csv")]
        if csvs:
            csvs.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            candidato = csvs[0]

            try:
                s1 = os.path.getsize(candidato)
                time.sleep(0.6)
                s2 = os.path.getsize(candidato)
                if s1 == s2 and s2 > 0:
                    return candidato
            except:
                pass

        time.sleep(0.4)

    raise TimeoutError("Download não finalizou a tempo (nenhum .csv pronto encontrado).")
'''

esperar_new = '''
def _esperar_download_csv(pasta, timeout_s=150, t0_download=None):
    t0 = time.time()
    if t0_download is None: t0_download = t0 - 2
    
    ignore_ext = (".crdownload", ".part", ".tmp")

    while time.time() - t0 < timeout_s:
        files = [os.path.join(pasta, f) for f in os.listdir(pasta)]
        files = [f for f in files if os.path.isfile(f)]

        if any(f.lower().endswith(ignore_ext) for f in files):
            time.sleep(0.5)
            continue

        csvs = [f for f in files if f.lower().endswith(".csv")]
        if csvs:
            csvs_recentes = [f for f in csvs if os.path.getmtime(f) >= (t0_download - 5.0)]
            if csvs_recentes:
                csvs_recentes.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                candidato = csvs_recentes[0]

                try:
                    s1 = os.path.getsize(candidato)
                    time.sleep(0.6)
                    s2 = os.path.getsize(candidato)
                    if s1 == s2 and s2 > 0:
                        return candidato
                except:
                    pass

        time.sleep(0.4)

    raise TimeoutError("Download não finalizou a tempo (nenhum .csv pronto encontrado).")
'''
code = code.replace(esperar_old.strip(), esperar_new.strip())

# 4. Update _mover_csv_para_pasta_final
mover_old = '''
def _mover_csv_para_pasta_final(csv_tmp_path, estacao, data_dia: datetime):
    pasta_final = os.path.join(PASTA_ORIGINAL, estacao["pasta"], data_dia.strftime("%Y"), data_dia.strftime("%m"))
    criar_pasta(pasta_final)

    nome_final = f"extracao_{estacao['nome']}_{data_dia.strftime('%Y-%m-%d')}.csv"
    final = os.path.join(pasta_final, nome_final)

    if os.path.abspath(csv_tmp_path) != os.path.abspath(final):
        try:
            shutil.move(csv_tmp_path, final)
        except Exception:
            shutil.copy2(csv_tmp_path, final)
    return final
'''

mover_new = '''
def _mover_csv_para_pasta_final(csv_tmp_path, estacao, data_dia: datetime):
    pasta_final = os.path.join(PASTA_ORIGINAL, estacao["pasta"], data_dia.strftime("%Y"), data_dia.strftime("%m"))
    criar_pasta(pasta_final)

    nome_final = f"extracao_{estacao['nome']}_{data_dia.strftime('%Y-%m-%d')}.csv"
    final = os.path.join(pasta_final, nome_final)

    if os.path.abspath(csv_tmp_path) != os.path.abspath(final):
        # Substituido move() por copy2(), garantindo que o Chrome consiga clicar pra abrir do buffer do download
        try:
            shutil.copy2(csv_tmp_path, final)
        except Exception:
            shutil.copy2(csv_tmp_path, final)
    return final
'''
code = code.replace(mover_old.strip(), mover_new.strip())

# 5. Update baixar_um_dia_com_driver (remove limpar_dir and pass t0)
baixar_old = '''
def baixar_um_dia_com_driver(nav, estacao: dict, data_dia: datetime):
    _limpar_dir(PASTA_TMP_DOWNLOAD)

    _open_url_com_retry(nav, URL, tentativas=4)

    _selecionar_estacao(nav, estacao)
    _selecionar_data(nav, data_dia)

    _clicar_visualizar_dados(nav)
    _clicar_baixar_dados(nav)

    csv_tmp = _esperar_download_csv(PASTA_TMP_DOWNLOAD, timeout_s=150)
    final = _mover_csv_para_pasta_final(csv_tmp, estacao, data_dia)

    _log(f"✔ Download concluído: {final}")
    return final
'''

baixar_new = '''
def baixar_um_dia_com_driver(nav, estacao: dict, data_dia: datetime):
    _open_url_com_retry(nav, URL, tentativas=4)

    _selecionar_estacao(nav, estacao)
    _selecionar_data(nav, data_dia)

    _clicar_visualizar_dados(nav)
    
    t0_down = time.time()
    _clicar_baixar_dados(nav)

    csv_tmp = _esperar_download_csv(PASTA_TMP_DOWNLOAD, timeout_s=150, t0_download=t0_down)
    final = _mover_csv_para_pasta_final(csv_tmp, estacao, data_dia)

    _log(f"✔ Download concluído: {final}")
    return final
'''
code = code.replace(baixar_old.strip(), baixar_new.strip())

# 6. Update rodar_intervalo_datas_todas_estacoes to take estacoes_selecionadas
rodar_old_sig = '''def rodar_intervalo_datas_todas_estacoes(data_ini: str, data_fim: str, tentativas_por_estacao=3):'''
rodar_new_sig = '''def rodar_intervalo_datas_todas_estacoes(data_ini: str, data_fim: str, estacoes_selecionadas: list, tentativas_por_estacao=3):'''

rodar_old_bod = '''
    d_ini = datetime.strptime(data_ini, "%Y-%m-%d")
    d_fim = datetime.strptime(data_fim, "%Y-%m-%d")
    todas = ESTACOES_FIXAS + ESTACOES_SCROLL
'''
rodar_new_bod = '''
    d_ini = datetime.strptime(data_ini, "%Y-%m-%d")
    d_fim = datetime.strptime(data_fim, "%Y-%m-%d")
    todas = estacoes_selecionadas
'''

code = code.replace(rodar_old_sig, rodar_new_sig)
code = code.replace(rodar_old_bod.strip(), rodar_new_bod.strip())

# 7. Replace def main()... and if __name__ == "__main__": with GUI
main_pattern = re.compile(r'def main\(\):.*', re.DOTALL)

gui_code = '''
class AppExtrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robô Extrator Meteorológico")
        self.geometry("750x650")
        self.configure(padx=15, pady=15)
        
        global GUI_LOG_CALLBACK
        GUI_LOG_CALLBACK = self.log_to_ui

        self.todas_estacoes = ESTACOES_FIXAS + ESTACOES_SCROLL
        
        self.create_widgets()
        
    def create_widgets(self):
        # Cabecalho
        lbl_titulo = ttk.Label(self, text="Extrator de Dados – Configuração", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=(0, 10))

        frame_datas = ttk.LabelFrame(self, text="Período de Extração", padding=10)
        frame_datas.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_datas, text="Data Inicial (AAAA-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ent_data_ini = ttk.Entry(frame_datas)
        self.ent_data_ini.grid(row=0, column=1, padx=5, pady=5)
        self.ent_data_ini.insert(0, DATA_INI)
        
        ttk.Label(frame_datas, text="Data Final (AAAA-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.ent_data_fim = ttk.Entry(frame_datas)
        self.ent_data_fim.grid(row=0, column=3, padx=5, pady=5)
        self.ent_data_fim.insert(0, DATA_FIM)
        
        frame_estacoes = ttk.LabelFrame(self, text="Seleção de Estações", padding=10)
        frame_estacoes.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.var_todas = tk.BooleanVar(value=True)
        chk_todas = ttk.Checkbutton(frame_estacoes, text="Selecionar Todas as Estações", variable=self.var_todas, command=self.toggle_todas)
        chk_todas.pack(anchor=tk.W, pady=(0, 5))
        
        scroll_frame = ttk.Frame(frame_estacoes)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_estacoes = tk.Listbox(scroll_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        self.listbox_estacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_estacoes.yview)
        
        for i, est in enumerate(self.todas_estacoes):
            self.listbox_estacoes.insert(tk.END, f"{i+1:02d} - {est['nome']}")
        
        self.listbox_estacoes.select_set(0, tk.END)
        self.listbox_estacoes.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        self.btn_iniciar = ttk.Button(frame_botoes, text="✨ INICIAR EXTRAÇÃO ✨", command=self.iniciar_extracao, padding=5)
        self.btn_iniciar.pack(expand=True)
        
        lbl_log = ttk.Label(self, text="Log de Execução:")
        lbl_log.pack(anchor=tk.W)
        self.txt_log = scrolledtext.ScrolledText(self, height=12, state=tk.DISABLED, font=("Consolas", 9), background="#f4f4f4")
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self.txt_log.insert(tk.END, "Aguardando início...\\n")
        
    def toggle_todas(self):
        if self.var_todas.get():
            self.listbox_estacoes.select_set(0, tk.END)
        else:
            self.listbox_estacoes.select_clear()
            
    def on_listbox_select(self, event):
        selecoes = self.listbox_estacoes.curselection()
        if len(selecoes) != len(self.todas_estacoes):
            self.var_todas.set(False)
        else:
            self.var_todas.set(True)
            
    def log_to_ui(self, msg):
        def _append():
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.insert(tk.END, msg + "\\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state=tk.DISABLED)
        self.after(0, _append)
        
    def iniciar_extracao(self):
        dt_ini = self.ent_data_ini.get().strip()
        dt_fim = self.ent_data_fim.get().strip()
        
        try:
            datetime.strptime(dt_ini, "%Y-%m-%d")
            datetime.strptime(dt_fim, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Data", "O formato da data deve ser YYYY-MM-DD")
            return
            
        selecoes = self.listbox_estacoes.curselection()
        if not selecoes:
            messagebox.showerror("Atenção", "Selecione pelo menos uma estação!")
            return
            
        estacoes_selecionadas = [self.todas_estacoes[i] for i in selecoes]
        
        self.btn_iniciar.config(state=tk.DISABLED, text="RODANDO... AGUARDE")
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state=tk.DISABLED)
        
        criar_pasta(PASTA_SAIDA)
        criar_pasta(PASTA_ORIGINAL)
        criar_pasta(PASTA_CORRIGIDO)
        criar_pasta(PASTA_EXCEL)
        criar_pasta(PASTA_GRAFICOS)
        criar_pasta(PASTA_DEBUG)
        criar_pasta(PASTA_TMP_DOWNLOAD)
        criar_pasta(PASTA_LOGS)
        
        _limpar_dir(PASTA_TMP_DOWNLOAD)
        _init_logger()
        
        t = threading.Thread(target=self._run_thread, args=(dt_ini, dt_fim, estacoes_selecionadas))
        t.daemon = True
        t.start()
        
    def _run_thread(self, dt_ini, dt_fim, estacoes_selecionadas):
        try:
            rodar_intervalo_datas_todas_estacoes(dt_ini, dt_fim, estacoes_selecionadas, tentativas_por_estacao=TENTATIVAS_POR_ESTACAO)
            _log("✅ Extração Finalizada com sucesso!")
            self.after(0, lambda: messagebox.showinfo("Concluído", "Extração finalizada com sucesso! Verifique a pasta saída."))
        except Exception as e:
            _error(f"Falha fatal: {type(e).__name__}: {e}")
            if _LOG_FILE:
                try:
                    with open(_LOG_FILE, "a", encoding="utf-8") as f:
                        f.write("\\n=== TRACEBACK ===\\n")
                        f.write(traceback.format_exc())
                        f.write("\\n")
                except:
                    pass
            self.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro crítico.\\nVerifique o último Log na pasta logs.\\n{e}"))
        finally:
            self.after(0, lambda: self.btn_iniciar.config(state=tk.NORMAL, text="✨ INICIAR EXTRAÇÃO ✨"))

if __name__ == "__main__":
    app = AppExtrator()
    app.mainloop()
'''

code = main_pattern.sub(gui_code, code)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)

print("ARQUIVO ATUALIZADO PELO PATCH PYTHON")
