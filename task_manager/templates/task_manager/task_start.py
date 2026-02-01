import psutil
import time
import os

for proc in psutil.process_iter(["pid", "name"]):
    if proc.info["name"] == "WINWORD.EXE":
        print(proc)


try:
    proc = psutil.Process(43116)
except psutil.NoSuchProcess:
    print("Proces s tímto PID neexistuje")
    exit()

# Vypis využití CPU a paměti každou sekundu 5x
for _ in range(5):
    cpu_percent = proc.cpu_percent(interval=1)  # % CPU za poslední 1 sekundu
    mem_info = proc.memory_info()  # objekt s pamětí
    print(f"CPU: {cpu_percent}%, Memory: {mem_info.rss / (1024**2):.2f} MB")

user = proc.username()
print(user)
start_time = proc.create_time()

# aktuální čas
current_time = time.time()

# doba běhu v sekundách
elapsed_time_sec = current_time - start_time

# převod na hodiny, minuty, sekundy
hours = int(elapsed_time_sec // 3600)
minutes = int((elapsed_time_sec % 3600) // 60)
seconds = int(elapsed_time_sec % 60)

print(f"Proces běží: {hours}h {minutes}m {seconds}s")

try:
    while True:
        cpu_percent = proc.cpu_percent(interval=None)  # okamžité využití CPU
        mem_info = proc.memory_info()
        mem_mb = mem_info.rss / (1024**2)  # převod na MB
        print(f"CPU: {cpu_percent:.1f}%, Memory: {mem_mb:.2f} MB")
        time.sleep(5)
except KeyboardInterrupt:
    print("Sledování ukončeno.")


path = r"C:\Users\blaze\Documents"
os.startfile(path)

# import time
# import os
# import pythoncom
# import win32com.client as win32

# # Nastavení pracovní složky
# working_directory = r"C:\Users\blaze\Documents\WordProjects"
# os.makedirs(working_directory, exist_ok=True)  # vytvoří složku, pokud neexistuje

# # Cesta k souboru
# doc_path = os.path.join(working_directory, "TestWord.docx")

# # Doba, po kterou necháme Word běžet (v sekundách)
# wait_time = 60  # např. 1 minuta

# # Inicializace COM
# pythoncom.CoInitialize()

# # Spuštění Wordu
# word = win32.Dispatch("Word.Application")
# word.Visible = True  # zobrazí Word okno

# # Nastavení výchozí pracovní cesty pro Word
# word.Options.DefaultFilePath(win32.constants.wdDocumentsPath)
# # alternativně: word.Options.DefaultFilePath(win32.constants.wdDocumentsPath) = working_directory
# # Pozn: COM API někdy vyžaduje konstanty; pro vlastní složku stačí SaveAs cesta

# # Vytvoření nového dokumentu
# doc = word.Documents.Add()

# # Přidání textu do dokumentu
# doc.Content.Text = "Toto je testovací dokument s nastavenou pracovní složkou."

# # Získání PID Word procesu
# pid = word.Application.HWND
# print("Word je spuštěný, PID:", pid)

# # Počkejme definovanou dobu
# print(f"Čekám {wait_time} sekund...")
# time.sleep(wait_time)

# # Uložit dokument do nastavené pracovní složky
# doc.SaveAs(doc_path)
# print(f"Dokument uložen: {doc_path}")

# # Zavřít dokument
# doc.Close(False)

# # Zavřít Word
# word.Quit()

# print("Word byl korektně ukončen.")
