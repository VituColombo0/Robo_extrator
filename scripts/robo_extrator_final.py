import os
import time
import shutil
import traceback
from datetime import datetime, timedelta

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import calendar

import numpy as np
import pandas as pd

from selenium import webdriver
import selenium.webdriver.edge.webdriver
import openpyxl
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

from webdriver_manager.microsoft import EdgeChromiumDriverManager

from scipy.interpolate import Akima1DInterpolator
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt


# =========================
# CONFIG "PRO" (NÃO MUDA O QUE FUNCIONOU)
# =========================
URL = "http://169.57.172.67:8501/Extrator_de_dados"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

PASTA_SAIDA = os.path.join(ROOT, "saida")
PASTA_ORIGINAL = os.path.join(PASTA_SAIDA, "ORIGINAL")
PASTA_CORRIGIDO = os.path.join(PASTA_SAIDA, "CORRIGIDO")
PASTA_EXCEL = os.path.join(PASTA_SAIDA, "EXCEL_TRATADO")
PASTA_GRAFICOS = os.path.join(PASTA_SAIDA, "GRAFICOS")
PASTA_DEBUG = os.path.join(PASTA_SAIDA, "DEBUG")
PASTA_LOGS = os.path.join(PASTA_SAIDA, "LOGS")

PASTA_TMP_DOWNLOAD = os.path.join(PASTA_SAIDA, "_DOWNLOAD_TMP")

# Organização opcional dos gráficos:
# True  => salva em subpastas por estação/ano/mês (sem mudar geração)
# False => mantém como está hoje (tudo em PASTA_GRAFICOS)
ORGANIZAR_GRAFICOS_POR_ESTACAO = False

# Modo execução:
# "TESTE" => usa TEST_DATA_INI/TEST_DATA_FIM
# "PRODUCAO" => você define DATA_INI/DATA_FIM
MODO = "TESTE"

TEST_DATA_INI = "2025-12-01"
TEST_DATA_FIM = "2025-12-03"

# Se estiver em produção, setar aqui:
DATA_INI = "2025-12-01"
DATA_FIM = "2025-12-03"

TENTATIVAS_POR_ESTACAO = 3

COLUNAS_NUM = ["delta_pluv", "temperatura", "umidade", "radiacao", "vel_vento", "dir_vento", "max_velocidade"]

ESTACOES_FIXAS = [
    {"nome": "Area 1 – Betânia", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[1]', "pasta": "extracao_Area 1 – Betânia"},
    {"nome": "Area 2 – Vila Curuçá-2", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[2]', "pasta": "extracao_Area 2 – Vila Curuçá-2"},
    {"nome": "Area 3 – Parque João Ramalho", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[3]', "pasta": "extracao_Area 3 – Parque João Ramalho"},
    {"nome": "Area 4 – Jardim Rina-2", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[4]', "pasta": "extracao_Area 4 – Jardim Rina-2"},
    {"nome": "Area 5 – Jardim Santo Antônio", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[5]', "pasta": "extracao_Area 5 – Jardim Santo Antônio"},
    {"nome": "Area 6 - Parque das Nações-2", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[6]', "pasta": "extracao_Area 6 - Parque das Nações-2"},
    {"nome": "Area 8 – PMSA", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[7]', "pasta": "extracao_Area 8 – PMSA"},
    {"nome": "Area 9 - Campestre", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[8]', "pasta": "extracao_Area 9 - Campestre"},
    {"nome": "Area 10 - Vila Palmares", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[9]', "pasta": "extracao_Area 10 - Vila Palmares"},
    {"nome": "Area 11 - Vila Floresta", "xpath": '/html/body/div[1]/div[2]/div/div/div/div/div/div/ul/div/div/li[10]', "pasta": "extracao_Area 11 - Vila Floresta"},
]

ESTACOES_SCROLL = [
    {"nome": "Area 12 - Defesa Civil", "indice_scroll": 10, "pasta": "extracao_Area 12 - Defesa Civil"},
    {"nome": "Area 13 - Jardim Stella", "indice_scroll": 11, "pasta": "extracao_Area 13 - Jardim Stella"},
    {"nome": "Area 14 - Jardim Silveira", "indice_scroll": 12, "pasta": "extracao_Area 14 - Jardim Silveira"},
    {"nome": "Area 15 - Guarará", "indice_scroll": 13, "pasta": "extracao_Area 15 - Guarará"},
    {"nome": "Area 16 – Premem", "indice_scroll": 14, "pasta": "extracao_Area 16 – Premem"},
    {"nome": "Area 17 - Jardim Santo André", "indice_scroll": 15, "pasta": "extracao_Area 17 - Jardim Santo André"},
    {"nome": "Area 18 - Homero Thon", "indice_scroll": 16, "pasta": "extracao_Area 18 - Homero Thon"},
    {"nome": "Area 19 - Jardim Marek", "indice_scroll": 17, "pasta": "extracao_Area 19 - Jardim Marek"},
    {"nome": "Area 20 - Sítio Dos Vianas", "indice_scroll": 18, "pasta": "extracao_Area 20 - Sítio Dos Vianas"},
    {"nome": "Area 21 – Sabina", "indice_scroll": 19, "pasta": "extracao_Area 21 – Sabina"},
    {"nome": "Area 22 - Bairro Jardim", "indice_scroll": 20, "pasta": "extracao_Area 22 - Bairro Jardim"},
    {"nome": "Area 23 – Utinga", "indice_scroll": 21, "pasta": "extracao_Area 23 – Utinga"},
    {"nome": "Area 24 - Jardim Bela Vista", "indice_scroll": 22, "pasta": "extracao_Area 24 - Jardim Bela Vista"},
    {"nome": "Area 25 - Parque Capuava", "indice_scroll": 23, "pasta": "extracao_Area 25 - Parque Capuava"},
    {"nome": "Area 26 - Parque Miami-2", "indice_scroll": 24, "pasta": "extracao_Area 26 - Parque Miami-2"},
]
TODAS_ESTACOES = ESTACOES_FIXAS + ESTACOES_SCROLL

# =========================
# LOG "PRO" (print + arquivo)
# =========================
_LOG_FILE = None

def criar_pasta(p):
    os.makedirs(p, exist_ok=True)

def _init_logger():
    global _LOG_FILE
    criar_pasta(PASTA_LOGS)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    _LOG_FILE = os.path.join(PASTA_LOGS, f"run_{ts}.log")
    with open(_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== LOG RUN {ts} ===\n")

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
                f.write(linha + "\n")
        except:
            pass

def _warn(msg):
    linha = f"[WARN] {msg}"
    print(linha)
    _escrever_gui(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\n")
        except:
            pass

def _error(msg):
    linha = f"[ERROR] {msg}"
    print(linha)
    _escrever_gui(linha)
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linha + "\n")
        except:
            pass


# =========================
# DEBUG AUTOMÁTICO (screenshot + html) QUANDO DER ERRO
# =========================
def _salvar_debug(nav, prefixo="falha"):
    try:
        criar_pasta(PASTA_DEBUG)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        png = os.path.join(PASTA_DEBUG, f"{prefixo}_{ts}.png")
        html = os.path.join(PASTA_DEBUG, f"{prefixo}_{ts}.html")

        try:
            nav.save_screenshot(png)
        except:
            png = None

        try:
            with open(html, "w", encoding="utf-8") as f:
                f.write(nav.page_source or "")
        except:
            html = None

        try:
            _warn(f"DEBUG current_url: {nav.current_url}")
            _warn(f"DEBUG title: {nav.title}")
        except:
            pass

        if png:
            _warn(f"DEBUG screenshot salvo em: {png}")
        if html:
            _warn(f"DEBUG html salvo em: {html}")
    except:
        pass


# =========================
# Funções originais (mantidas) + incrementos sem alterar lógica
# =========================
def _limpar_dir(pasta):
    criar_pasta(pasta)
    for f in os.listdir(pasta):
        try:
            os.remove(os.path.join(pasta, f))
        except:
            pass

def _edge_driver(download_dir):
    criar_pasta(download_dir)
    opts = Options()
    opts.use_chromium = True
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--start-maximized")
    driver = webdriver.Edge(service=Service(), options=opts)
    driver.set_page_load_timeout(90)
    return driver

def _safe_click(nav, element):
    try:
        element.click()
        return
    except ElementClickInterceptedException:
        pass
    except StaleElementReferenceException:
        pass

    try:
        nav.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", element)
        time.sleep(0.15)
        nav.execute_script("arguments[0].click();", element)
        return
    except Exception:
        pass

    ActionChains(nav).move_to_element(element).pause(0.1).click(element).perform()

def _open_url_com_retry(nav, url, tentativas=4):
    last = None
    for i in range(1, tentativas + 1):
        try:
            _log(f"Abrindo URL (tentativa {i}/{tentativas})...")
            nav.get(url)
            time.sleep(1.5)
            return
        except Exception as e:
            last = e
            time.sleep(2.0)
    raise last

def _esperar_download_csv(pasta, timeout_s=150, t0_download=None):
    t0 = time.time()
    if t0_download is None:
        t0_download = t0 - 2
    
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

def _abrir_dropdown_estacoes(nav):
    el = WebDriverWait(nav, 35).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-baseweb="select"]')))
    _safe_click(nav, el)
    time.sleep(0.4)

def _selecionar_estacao(nav, estacao):
    _abrir_dropdown_estacoes(nav)

    if "xpath" in estacao:
        el = WebDriverWait(nav, 35).until(EC.element_to_be_clickable((By.XPATH, estacao["xpath"])))
        _safe_click(nav, el)
        time.sleep(0.35)
        return

    act = ActionChains(nav)
    for _ in range(int(estacao["indice_scroll"])):
        act.send_keys(Keys.ARROW_DOWN).pause(0.10)
    act.send_keys(Keys.ENTER).pause(0.15).send_keys(Keys.ENTER).perform()
    time.sleep(0.5)

def _set_date_by_typing(nav, data_dia: datetime):
    inp = WebDriverWait(nav, 35).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Select a date."]'))
    )
    _safe_click(nav, inp)
    time.sleep(0.15)

    s = data_dia.strftime("%Y/%m/%d")

    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.BACKSPACE)
    inp.send_keys(s)
    inp.send_keys(Keys.ENTER)
    time.sleep(0.6)

def _selecionar_data(nav, data_dia: datetime):
    try:
        _set_date_by_typing(nav, data_dia)
        return
    except Exception:
        pass

    inp = WebDriverWait(nav, 35).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Select a date."]'))
    )
    _safe_click(nav, inp)
    time.sleep(0.5)

    el_ano = WebDriverWait(nav, 35).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "202")]'))
    )
    _safe_click(nav, el_ano)
    time.sleep(0.3)

    ano = data_dia.year
    el_ano_item = WebDriverWait(nav, 35).until(EC.element_to_be_clickable((By.XPATH, f'//li[text()="{ano}"]')))
    _safe_click(nav, el_ano_item)
    time.sleep(0.3)

    mes_num = data_dia.month
    dia = data_dia.day
    mes_en = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"][mes_num]

    el_mes_dropdown = WebDriverWait(nav, 35).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[role="presentation"]'))
    )
    _safe_click(nav, el_mes_dropdown)
    time.sleep(0.25)

    el_mes_item = WebDriverWait(nav, 35).until(EC.element_to_be_clickable((By.XPATH, f'//li[text()="{mes_en}"]')))
    _safe_click(nav, el_mes_item)
    time.sleep(0.25)

    el_dia = WebDriverWait(nav, 35).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@role="gridcell" and div[text()="{dia}"]]'))
    )
    _safe_click(nav, el_dia)
    time.sleep(0.6)

def _clicar_visualizar_dados(nav):
    xpath = '//button[normalize-space(.)="Visualizar dados"]'
    btn = WebDriverWait(nav, 60).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    _safe_click(nav, btn)
    time.sleep(0.6)

def _clicar_baixar_dados(nav):
    xpath = '//button[normalize-space(.)="Baixar dados"]'
    btn = WebDriverWait(nav, 75).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    _safe_click(nav, btn)
    time.sleep(0.5)

def gerar_horarios_completos(base):
    return [base + timedelta(minutes=5 * i) for i in range(288)]

def ajustar_radiacao(df):
    df["radiacao"] = pd.to_numeric(df["radiacao"], errors="coerce")
    
    # Ensure no negative values directly from raw data
    df.loc[df["radiacao"] < 0, "radiacao"] = 0.0
    
    df["hora"] = df["data_hora"].dt.hour + df["data_hora"].dt.minute / 60
    
    # Clamp nighttime radiation to exactly 0 to prevent issues like 100 radiation at 3 AM
    mask_noturna = (df["hora"] < 6) | (df["hora"] > 18)
    df.loc[mask_noturna, "radiacao"] = 0.0
    
    # Interpolate missing values slightly to avoid breaking the curve
    df["radiacao"] = df["radiacao"].interpolate(limit_direction="both")
    
    df["radiacao"] = df["radiacao"].clip(lower=0).round(2)
    df.drop(columns=["hora"], inplace=True)
    return df

def evitar_temperaturas_repetidas(df):
    df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")
    # Limita valores totalmente absurdos, mas confia no dado bruto real
    df.loc[(df["temperatura"] > 50) | (df["temperatura"] < -5), "temperatura"] = np.nan

    # Só interpola buracos reais, nao recria dados aleatórios destruindo os valores verdadeiros
    df["temperatura"] = df["temperatura"].interpolate(limit_direction="both").round(2)
    return df

def corrigir_csv(caminho_csv, pasta_corrigido, data_req_dia=None):
    criar_pasta(pasta_corrigido)

    df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
    df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce").dt.floor("5min")
    df.dropna(subset=["data_hora"], inplace=True)

    if data_req_dia is not None:
        data_dia = pd.Timestamp(data_req_dia).floor("D")
    else:
        data_dia = df["data_hora"].min().floor("D")
        
    horarios = pd.DataFrame({"data_hora": gerar_horarios_completos(data_dia.to_pydatetime())})
    df = pd.merge(horarios, df, on="data_hora", how="left")

    for col in COLUNAS_NUM:
        if col in df.columns:
            df[col] = _to_numeric_series(df[col])

    df = ajustar_radiacao(df)
    df = evitar_temperaturas_repetidas(df)

    for col in COLUNAS_NUM:
        if col not in ["temperatura", "radiacao"]:
            df[col] = df[col].fillna(0).round(2)

    df["data_hora"] = df["data_hora"].dt.strftime("%d/%m/%Y %H:%M")
    df = df[["data_hora"] + COLUNAS_NUM]

    nome_out = os.path.basename(caminho_csv)
    out_path = os.path.join(pasta_corrigido, nome_out)
    df.to_csv(out_path, sep=";", index=False, encoding="utf-8")
    return out_path

def _to_numeric_series(s):
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_numeric(s, errors="coerce")
    
    def fix_val(val):
        if pd.isna(val): return val
        v = str(val).strip()
        if ',' in v:
            return v.replace('.', '').replace(',', '.')
        return v
        
    return pd.to_numeric(s.apply(fix_val), errors="coerce")

def tratar_akima_savgol(df, coluna, janela=21, poly=3):
    y = _to_numeric_series(df[coluna]).astype(float)
    x = np.arange(len(y), dtype=float)

    mask = np.isfinite(y)
    if mask.sum() < 5:
        return pd.Series(y).round(2)

    xi = x[mask]
    yi = y[mask]

    try:
        interp = Akima1DInterpolator(xi, yi)
        y_interp = interp(x)
    except Exception:
        y_interp = pd.Series(y).interpolate(limit_direction="both").to_numpy(dtype=float)

    y_interp = np.where(np.isfinite(y_interp), y_interp, np.nan)
    y_interp = pd.Series(y_interp).interpolate(limit_direction="both").to_numpy(dtype=float)

    n = len(y_interp)
    win = janela + (0 if janela % 2 == 1 else 1)
    if win > n:
        win = n if n % 2 == 1 else n - 1
    if win < 5:
        return pd.Series(y_interp).round(2)

    try:
        y_f = savgol_filter(y_interp, window_length=win, polyorder=min(poly, win - 2), mode="interp")
    except Exception:
        y_f = y_interp

    # Prevenir que o filtro crie anomalias negativas onde não devem existir
    if coluna in ["radiacao", "vel_vento", "max_velocidade", "delta_pluv", "umidade"]:
        y_f = np.clip(y_f, a_min=0.0, a_max=None)
        
    return pd.Series(y_f).round(2)

def gerar_excel_tratado(caminho_csv_corrigido, pasta_excel):
    criar_pasta(pasta_excel)

    df = pd.read_csv(caminho_csv_corrigido, sep=";", encoding="utf-8")
    df["data_hora_dt"] = pd.to_datetime(df["data_hora"], format="%d/%m/%Y %H:%M", errors="coerce")

    for col in COLUNAS_NUM:
        if col in df.columns:
            df[f"{col}_akima_savgol"] = tratar_akima_savgol(df, col)

    nome = os.path.splitext(os.path.basename(caminho_csv_corrigido))[0]
    out_xlsx = os.path.join(pasta_excel, f"{nome}_TRATADO.xlsx")
    df.to_excel(out_xlsx, index=False)
    return out_xlsx

def gerar_graficos_validacao(caminho_excel_tratado, pasta_graficos):
    criar_pasta(pasta_graficos)

    df = pd.read_excel(caminho_excel_tratado)
    x = df["data_hora_dt"] if "data_hora_dt" in df.columns else np.arange(len(df))
    base = os.path.splitext(os.path.basename(caminho_excel_tratado))[0]

    for col in COLUNAS_NUM:
        c2 = f"{col}_akima_savgol"
        if col not in df.columns or c2 not in df.columns:
            continue

        plt.figure()
        plt.plot(x, df[col], label=col)
        plt.plot(x, df[c2], label=c2)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        out_png = os.path.join(pasta_graficos, f"{base}_{col}.png")
        plt.savefig(out_png, dpi=140)
        plt.close()

def _pasta_graficos_para_estacao(estacao, data_dia: datetime):
    if not ORGANIZAR_GRAFICOS_POR_ESTACAO:
        return PASTA_GRAFICOS
    return os.path.join(PASTA_GRAFICOS, estacao["pasta"], data_dia.strftime("%Y"), data_dia.strftime("%m"))

def processar_csv_baixado(caminho_in, estacao, data_dia: datetime, stats=None):
    pasta_corr = os.path.join(PASTA_CORRIGIDO, estacao["pasta"], data_dia.strftime("%Y"), data_dia.strftime("%m"))
    pasta_excel = os.path.join(PASTA_EXCEL, estacao["pasta"], data_dia.strftime("%Y"), data_dia.strftime("%m"))

    csv_corr = corrigir_csv(caminho_in, pasta_corr, data_req_dia=data_dia)
    _log(f"✔ CSV corrigido salvo: {csv_corr}")

    xlsx = gerar_excel_tratado(csv_corr, pasta_excel)
    _log(f"✔ Excel tratado salvo: {xlsx}")

    pasta_graf = _pasta_graficos_para_estacao(estacao, data_dia)
    gerar_graficos_validacao(xlsx, pasta_graf)
    _log(f"✔ Gráficos salvos em: {pasta_graf}")

    if stats is not None:
        stats["csv_original"] += 1
        stats["csv_corrigido"] += 1
        stats["excels"] += 1
        stats["graficos_lotes"] += 1

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

def _daterange(ini: datetime, fim: datetime):
    d = ini
    while d <= fim:
        yield d
        d += timedelta(days=1)

def rodar_intervalo_datas_todas_estacoes(data_ini: str, data_fim: str, estacoes_selecionadas: list, tentativas_por_estacao=3):
    _log("=== MODO: EXTRAÇÃO COM ESTAÇÕES SELECIONADAS ===")
    _log(f"Período: {data_ini} até {data_fim}")
    _log("")

    d_ini = datetime.strptime(data_ini, "%Y-%m-%d")
    d_fim = datetime.strptime(data_fim, "%Y-%m-%d")
    todas = estacoes_selecionadas

    stats = {
        "estacoes_ok": 0,
        "estacoes_falha": 0,
        "dias": 0,
        "csv_original": 0,
        "csv_corrigido": 0,
        "excels": 0,
        "graficos_lotes": 0,
        "falhas": [],
    }

    nav = _edge_driver(PASTA_TMP_DOWNLOAD)
    t_start = time.time()
    try:
        for d in _daterange(d_ini, d_fim):
            stats["dias"] += 1
            _log(f"===== DIA {d.strftime('%Y-%m-%d')} =====")

            for est in todas:
                _log(f"--- Estação: {est['nome']} ---")

                ok = False
                last_exc = None
                for k in range(1, tentativas_por_estacao + 1):
                    try:
                        caminho = baixar_um_dia_com_driver(nav, est, d)
                        processar_csv_baixado(caminho, est, d, stats=stats)
                        _log("")
                        ok = True
                        stats["estacoes_ok"] += 1
                        break
                    except Exception as e:
                        last_exc = e
                        _warn(f"Falhou (tentativa {k}/{tentativas_por_estacao}): {type(e).__name__}: {e}")
                        _salvar_debug(nav, prefixo="extracao_falhou")
                        time.sleep(1.5)

                if not ok:
                    stats["estacoes_falha"] += 1
                    stats["falhas"].append({
                        "dia": d.strftime("%Y-%m-%d"),
                        "estacao": est["nome"],
                        "erro": f"{type(last_exc).__name__}: {last_exc}",
                    })
                    _warn(f"⚠ Estação pulada após {tentativas_por_estacao} tentativas: {est['nome']}")
                    _log("")
    finally:
        try:
            nav.quit()
        except:
            pass

        # Resumo final "PRO"
        dur = time.time() - t_start
        _log("=== RESUMO FINAL ===")
        _log(f"Dias processados: {stats['dias']}")
        _log(f"Sucessos (estação-dia): {stats['estacoes_ok']}")
        _log(f"Falhas (estação-dia): {stats['estacoes_falha']}")
        _log(f"CSV originais: {stats['csv_original']}")
        _log(f"CSV corrigidos: {stats['csv_corrigido']}")
        _log(f"Excels gerados: {stats['excels']}")
        _log(f"Lotes de gráficos: {stats['graficos_lotes']}")
        _log(f"Tempo total: {dur:.1f}s")

        if stats["falhas"]:
            criar_pasta(PASTA_DEBUG)
            falhas_csv = os.path.join(PASTA_DEBUG, "falhas_resumo.csv")
            pd.DataFrame(stats["falhas"]).to_csv(falhas_csv, index=False, encoding="utf-8")
            _warn(f"Resumo de falhas salvo em: {falhas_csv}")

        if _LOG_FILE:
            _log(f"Log completo salvo em: {_LOG_FILE}")


class AppExtrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robô Extrator Meteorológico")
        self.geometry("750x650")
        self.configure(padx=15, pady=15)
        
        global GUI_LOG_CALLBACK
        GUI_LOG_CALLBACK = self.log_to_ui

        self.todas_estacoes = TODAS_ESTACOES
        
        self.create_widgets()
        
    def create_widgets(self):
        lbl_titulo = ttk.Label(self, text="Extrator de Dados Meteorológicos", font=("Segoe UI", 16, "bold"))
        lbl_titulo.pack(pady=(5, 15))

        # --- FRAME DE DATAS ---
        frame_datas = ttk.LabelFrame(self, text="Filtro de Período", padding=15)
        frame_datas.pack(fill=tk.X, pady=5)
        
        self.var_modo_data = tk.StringVar(value="intervalo")
        
        def criar_radio(linha, valor, texto, widget_extra=None, widget_extra2=None, label_extra=None):
            rb = ttk.Radiobutton(frame_datas, text=texto, value=valor, variable=self.var_modo_data, command=self.atualizar_campos_data)
            rb.grid(row=linha, column=0, sticky=tk.W, pady=3)
            
            if widget_extra:
                widget_extra.grid(row=linha, column=1, padx=5, sticky=tk.W)
            if label_extra:
                label_extra.grid(row=linha, column=2, padx=2, sticky=tk.W)
            if widget_extra2:
                widget_extra2.grid(row=linha, column=3, padx=5, sticky=tk.W)

        self.ent_dia_unico = ttk.Entry(frame_datas, width=12)
        self.ent_dia_unico.insert(0, datetime.now().strftime("%Y-%m-%d"))
        criar_radio(0, "dia", "Um dia específico:", self.ent_dia_unico)
        
        self.ent_data_ini = ttk.Entry(frame_datas, width=12)
        self.ent_data_ini.insert(0, DATA_INI)
        lbl_ate = ttk.Label(frame_datas, text="até")
        self.ent_data_fim = ttk.Entry(frame_datas, width=12)
        self.ent_data_fim.insert(0, DATA_FIM)
        criar_radio(1, "intervalo", "Intervalo:", self.ent_data_ini, self.ent_data_fim, lbl_ate)
        
        criar_radio(2, "hoje", "De hoje em diante")
        
        self.ent_mes = ttk.Entry(frame_datas, width=8)
        self.ent_mes.insert(0, datetime.now().strftime("%Y-%m"))
        criar_radio(3, "mes", "Um mês específico (AAAA-MM):", self.ent_mes)
        
        self.ent_n_dias = ttk.Entry(frame_datas, width=5)
        self.ent_n_dias.insert(0, "5")
        lbl_dias = ttk.Label(frame_datas, text="dias")
        criar_radio(4, "ultimos", "Últimos N dias:", self.ent_n_dias, None, lbl_dias)

        frame_estacoes = ttk.LabelFrame(self, text="Seleção de Estações", padding=10)
        frame_estacoes.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.var_todas = tk.BooleanVar(value=False)
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
        
        self.listbox_estacoes.selection_clear(0, tk.END)
        self.listbox_estacoes.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        style = ttk.Style()
        style.configure("Exec.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        self.btn_iniciar = ttk.Button(frame_botoes, text="🚀 INICIAR EXTRAÇÃO", style="Exec.TButton", command=self.iniciar_extracao)
        self.btn_iniciar.pack(expand=True, fill=tk.X, padx=50)
        
        lbl_log = ttk.Label(self, text="Log de Execução:")
        lbl_log.pack(anchor=tk.W)
        self.txt_log = scrolledtext.ScrolledText(self, height=12, state=tk.DISABLED, font=("Consolas", 9), background="#f4f4f4")
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self.txt_log.insert(tk.END, "Aguardando início...\n")
        
        self.atualizar_campos_data()
        
    def atualizar_campos_data(self):
        modo = self.var_modo_data.get()
        self.ent_dia_unico.config(state=tk.NORMAL if modo == "dia" else tk.DISABLED)
        self.ent_data_ini.config(state=tk.NORMAL if modo == "intervalo" else tk.DISABLED)
        self.ent_data_fim.config(state=tk.NORMAL if modo == "intervalo" else tk.DISABLED)
        self.ent_mes.config(state=tk.NORMAL if modo == "mes" else tk.DISABLED)
        self.ent_n_dias.config(state=tk.NORMAL if modo == "ultimos" else tk.DISABLED)

    def toggle_todas(self):
        if self.var_todas.get():
            self.listbox_estacoes.select_set(0, tk.END)
        else:
            self.listbox_estacoes.selection_clear(0, tk.END)
            
    def on_listbox_select(self, event):
        selecoes = self.listbox_estacoes.curselection()
        if len(selecoes) != len(self.todas_estacoes):
            self.var_todas.set(False)
        else:
            self.var_todas.set(True)
            
    def log_to_ui(self, msg):
        def _append():
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.insert(tk.END, msg + "\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state=tk.DISABLED)
        self.after(0, _append)
        
    def iniciar_extracao(self):
        modo = self.var_modo_data.get()
        hoje = datetime.now()
        
        try:
            if modo == "dia":
                dt_ini = self.ent_dia_unico.get().strip()
                datetime.strptime(dt_ini, "%Y-%m-%d")
                dt_fim = dt_ini
                
            elif modo == "intervalo":
                dt_ini = self.ent_data_ini.get().strip()
                dt_fim = self.ent_data_fim.get().strip()
                datetime.strptime(dt_ini, "%Y-%m-%d")
                datetime.strptime(dt_fim, "%Y-%m-%d")
                
            elif modo == "hoje":
                dt_ini = hoje.strftime("%Y-%m-%d")
                dt_fim = hoje.strftime("%Y-%m-%d")
                
            elif modo == "mes":
                mes_str = self.ent_mes.get().strip()
                dt_mes = datetime.strptime(mes_str, "%Y-%m")
                ultimo_dia = calendar.monthrange(dt_mes.year, dt_mes.month)[1]
                dt_ini = f"{dt_mes.year}-{dt_mes.month:02d}-01"
                dt_fim = f"{dt_mes.year}-{dt_mes.month:02d}-{ultimo_dia:02d}"
                
            elif modo == "ultimos":
                n_str = self.ent_n_dias.get().strip()
                n = int(n_str)
                dt_ini = (hoje - timedelta(days=n)).strftime("%Y-%m-%d")
                dt_fim = hoje.strftime("%Y-%m-%d")
                
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data ou número inválido para o filtro escolhido.")
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
                        f.write("\n=== TRACEBACK ===\n")
                        f.write(traceback.format_exc())
                        f.write("\n")
                except:
                    pass
            self.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro crítico.\nVerifique o último Log na pasta logs.\n{e}"))
        finally:
            self.after(0, lambda: self.btn_iniciar.config(state=tk.NORMAL, text="🚀 INICIAR EXTRAÇÃO"))

if __name__ == "__main__":
    app = AppExtrator()
    app.mainloop()
