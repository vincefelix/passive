import tkinter as tk
from tkinter import messagebox
import requests
import re
import os
import aiohttp
import asyncio
import json
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time

def configure_driver():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def wait_for_page_to_load(driver, timeout=5):
    time_elapsed = 0
    while time_elapsed < timeout:
        if driver.execute_script("return document.readyState") == "complete":
            break
        time.sleep(1)
        time_elapsed += 1

def search_pages_jaunes():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom complet.")
        return

    driver = configure_driver()
    contact_found = False 

    try:
        url = f"https://www.pagesjaunes.fr/pagesblanches/r/{name.replace(' ', '.').lower()}/"
        driver.get(url)
        wait_for_page_to_load(driver)
        print(f"URL chargée : {url}")

        try:
            wait = WebDriverWait(driver, 5)
            user = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.bi")))
            contact_found = True  # Contact trouvé sur PagesJaunes

            # Extraction des informations
            try:
                full_name = user.find_element(By.CSS_SELECTOR, "a.bi-denomination h3").text
            except NoSuchElementException:
                full_name = "Nom non trouvé"

            try:
                address = user.find_element(By.CSS_SELECTOR, "div.bi-address a").text
                address = address.replace("Voir le plan", "")
            except NoSuchElementException:
                address = "Adresse non trouvée"

            try:
                phone_number = driver.execute_script("""
                    let numberElement = document.querySelector('div.number-contact span');
                    return numberElement ? numberElement.textContent.trim() : 'Téléphone non trouvé';
                """)
            except Exception as js_exception:
                print(f"Erreur JavaScript : {js_exception}")
                phone_number = "Téléphone non trouvé"

            # Résultat de la recherche sur PagesJaunes
            result = {
                "Nom complet": full_name,
                "Adresse": address,
                "Téléphone": phone_number
            }
            output_label.config(text=json.dumps(result, indent=4, ensure_ascii=False))
            save_results(result)

        except TimeoutException:
            print("Résultats introuvables sur PagesJaunes.")

    finally:
        driver.quit()

    # Étape 2 : Si pas trouvé sur PagesJaunes, rechercher dans le fichier JSON
    if not contact_found:
        print("Recherche dans le fichier JSON...")
        json_result = search_in_json(name)
        if json_result:
            contact_found = True
            result = {
                "Nom complet": f"{json_result['prenom']} {json_result['nom']}",
                "Adresse": json_result.get("adresse", "Adresse non disponible"),
                "Téléphone": json_result.get("telephone", "Téléphone non disponible")
            }
            output_label.config(text=json.dumps(result, indent=4, ensure_ascii=False))
            save_results(result)

    if not contact_found:
        result = {
            "Message": f"Contact '{name}' non trouvé ni sur PagesJaunes, ni dans le fichier JSON."
        }
        output_label.config(text=json.dumps(result, indent=4, ensure_ascii=False))
        save_results(result)

# ----------------- Recherche par IP -----------------
def search_ip():
    ip = ip_entry.get().strip()
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
        messagebox.showerror("Erreur", "Adresse IP invalide.")
        return

    response = requests.get(f"https://ipinfo.io/{ip}/json")
    if response.status_code == 200:
        data = response.json()
        isp = data.get('org', 'N/A')
        city = data.get('city', 'N/A')
        region = data.get('region', 'N/A')
        country = data.get('country', 'N/A')
        loc = data.get('loc', 'N/A')
        result = {
            "ISP": isp,
            "Ville": city,
            "Région": region,
            "Pays": country,
            "Localisation (Lat, Lon)": loc
        }
        output_label.config(text=json.dumps(result, indent=4, ensure_ascii=False))
        save_results(result)
    else:
        messagebox.showerror("Erreur", "Impossible de récupérer les données IP.")

# ----------------- Recherche par Username -----------------
async def search_username_async(username):
    platforms = [
        "https://facebook.com/",
        "https://twitter.com/",
        "https://linkedin.com/in/",
        "https://instagram.com/",
        "https://github.com/",
        "https://www.youtube.com/",
        "https://www.tiktok.com/@",
    ]
    result = {"Recherche Username": username}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for platform in platforms:
            url = f"{platform}{username}"
            tasks.append(fetch_status(session, url, platform))
        statuses = await asyncio.gather(*tasks)
        for status in statuses:
            result.update(status)
    output_label.config(text=json.dumps(result, indent=4, ensure_ascii=False))
    save_results(result)

async def fetch_status(session, url, platform):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return {platform: "Trouvé"}
            else:
                return {platform: "Non trouvé"}
    except Exception:
        return {platform: "Erreur lors de la recherche"}

def search_username():
    username = username_entry.get().strip().replace("@", "")
    if not username:
        messagebox.showerror("Erreur", "Veuillez entrer un nom d'utilisateur.")
        return
    asyncio.run(search_username_async(username))


def search_in_json(full_name):
    try:
        with open("contact.json", "r", encoding="utf-8") as json_file:
            contacts = json.load(json_file)
        full_name_lower = full_name.lower()
        for contact in contacts:
            contact_full_name = f"{contact.get('prenom', '').lower()} {contact.get('nom', '').lower()}"
            if contact_full_name == full_name_lower:
                return contact
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier JSON : {e}")
    return None

# ----------------- Sauvegarde des résultats -----------------
def save_results(data):
    if not os.path.exists("found"):
        os.makedirs("found")
    text_filename = os.path.join("found", "result.txt")
    if os.path.exists(text_filename):
        count = len([f for f in os.listdir("found") if f.startswith('result') and f.endswith('.txt')]) + 1
        text_filename = os.path.join("found", f"result{count}.txt")
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        for key, value in data.items():
            text_file.write(f"{key}: {value}\n")
    json_filename = os.path.join("found", "result.json")
    if os.path.exists(json_filename):
        count = len([f for f in os.listdir("found") if f.startswith('result') and f.endswith('.json')]) + 1
        json_filename = os.path.join("found", f"result{count}.json")
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Résultats sauvegardés dans {text_filename} et {json_filename}")

# ----------------- Interface Tkinter -----------------
root = tk.Tk()
root.title("Outil OSINT Passif Avancé")
root.geometry("500x600")

tk.Label(root, text="Recherche par IP:").pack(pady=5)
ip_entry = tk.Entry(root)
ip_entry.pack(pady=5)
tk.Button(root, text="Rechercher IP", command=search_ip).pack(pady=5)

tk.Label(root, text="Recherche par Nom Complet (PagesJaunes ou JSON):").pack(pady=5)
name_entry = tk.Entry(root)
name_entry.pack(pady=5)
tk.Button(root, text="Rechercher sur PagesJaunes ou JSON", command=search_pages_jaunes).pack(pady=5)

tk.Label(root, text="Recherche par Nom d'Utilisateur:").pack(pady=5)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)
tk.Button(root, text="Rechercher Username", command=search_username).pack(pady=5)

output_label = tk.Label(root, text="", justify="left", wraplength=480, anchor="w")
output_label.pack(pady=10)

root.mainloop()
