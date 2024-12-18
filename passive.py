import tkinter as tk
from tkinter import messagebox
import argparse
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

# Configuration du driver Selenium
def configure_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def wait_for_page_to_load(driver, timeout=2):
    time_elapsed = 0
    while time_elapsed < timeout:
        if driver.execute_script("return document.readyState") == "complete":
            break
        time.sleep(1)
        time_elapsed += 1

# Recherche sur PagesJaunes
def search_pages_jaunes(name):
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
            contact_found = True

            full_name = user.find_element(By.CSS_SELECTOR, "a.bi-denomination h3").text
            address = user.find_element(By.CSS_SELECTOR, "div.bi-address a").text.replace("Voir le plan", "")
            phone_number = driver.execute_script("""
                let numberElement = document.querySelector('div.number-contact span');
                return numberElement ? numberElement.textContent.trim() : 'Téléphone non trouvé';
            """)

            result = {
                "Nom complet": full_name,
                "Adresse": address,
                "Téléphone": phone_number
            }
            save_results(result)
            return result

        except TimeoutException:
            print("Résultats introuvables sur PagesJaunes.")
    finally:
        driver.quit()

    # Recherche dans le fichier JSON
    if not contact_found:
        print("Recherche dans le fichier JSON...")
        json_result = search_in_json(name)
        if json_result:
            result = {
                "Nom complet": f"{json_result['prenom']} {json_result['nom']}",
                "Adresse": json_result.get("adresse", "Adresse non disponible"),
                "Téléphone": json_result.get("telephone", "Téléphone non disponible")
            }
            save_results(result)
            return result

    return {"Message": f"Contact '{name}' non trouvé."}

# Recherche d'une adresse IP
def search_ip(ip):
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
        raise ValueError("Adresse IP invalide.")

    response = requests.get(f"https://ipinfo.io/{ip}/json")
    if response.status_code == 200:
        data = response.json()
        result = {
            "ISP": data.get('org', 'N/A'),
            "Ville": data.get('city', 'N/A'),
            "Région": data.get('region', 'N/A'),
            "Pays": data.get('country', 'N/A'),
            "Localisation (Lat, Lon)": data.get('loc', 'N/A')
        }
        save_results(result)
        return result
    else:
        raise ValueError("Impossible de récupérer les données IP.")

# Recherche par username
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
        tasks = [fetch_status(session, f"{platform}{username}", platform) for platform in platforms]
        statuses = await asyncio.gather(*tasks)
        for status in statuses:
            result.update(status)
    save_results(result)
    return result

async def fetch_status(session, url, platform):
    try:
        async with session.get(url) as response:
            return {platform: "Trouvé" if response.status == 200 else "Non trouvé"}
    except Exception:
        return {platform: "Erreur lors de la recherche"}

# Recherche dans un fichier JSON
def search_in_json(full_name):
    if not os.path.exists("contact.json"):
        raise FileNotFoundError("Le fichier 'contact.json' est introuvable.")

    with open("contact.json", "r", encoding="utf-8") as json_file:
        contacts = json.load(json_file)
    full_name_lower = full_name.lower()
    for contact in contacts:
        contact_full_name = f"{contact.get('prenom', '').lower()} {contact.get('nom', '').lower()}"
        if contact_full_name == full_name_lower:
            return contact
    return None

# Sauvegarde des résultats
# def save_results(data):
#     if not os.path.exists("found"):
#         os.makedirs("found")
#     filename = os.path.join("found", "result.txt")
#     with open(filename, 'w', encoding='utf-8') as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)
#     print(f"Résultats sauvegardés dans {filename}")

def save_results(data):
    print(data)
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

# Interface graphique
def launch_gui():
    root = tk.Tk()
    root.title("Outil OSINT")
    root.geometry("500x600")

    tk.Label(root, text="Recherche par IP:").pack(pady=5)
    ip_entry = tk.Entry(root)
    ip_entry.pack(pady=5)
    tk.Button(
        root,
        text="Rechercher IP",
        command=lambda: display_result(search_ip(ip_entry.get().strip()))
    ).pack(pady=5)

    tk.Label(root, text="Recherche par Nom Complet (PagesJaunes ou JSON):").pack(pady=5)
    name_entry = tk.Entry(root)
    name_entry.pack(pady=5)
    tk.Button(
        root,
        text="Rechercher sur PagesJaunes ou JSON",
        command=lambda: display_result(search_pages_jaunes(name_entry.get().strip()))
    ).pack(pady=5)

    tk.Label(root, text="Recherche par Nom d'Utilisateur:").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)
    tk.Button(
        root,
        text="Rechercher Username",
        command=lambda: asyncio.run(display_username_results(username_entry.get().strip()))
    ).pack(pady=5)
    
    global output_label
    output_label = tk.Label(root, text="", justify="left", wraplength=480, anchor="w", bg="lightgrey", relief="sunken", padx=10, pady=10)
    output_label.pack(pady=10, fill="both", expand=True)

    root.mainloop()

def display_result(result):
    """
    Met à jour l'output_label avec les résultats au format texte ou JSON.
    """
    if isinstance(result, dict):
        result_text = json.dumps(result, indent=4, ensure_ascii=False)
    else:
        result_text = str(result)
    output_label.config(text=result_text)

async def display_username_results(username):
    """
    Récupère les résultats des recherches par username et met à jour l'output_label.
    """
    result = await search_username_async(username)
    display_result(result)


# Arguments via le terminal
def main():
    parser = argparse.ArgumentParser(description="Outil OSINT Passif")
    parser.add_argument("-fn", "--fullname", help="Recherche par nom complet")
    parser.add_argument("-ip", "--ipaddress", help="Recherche par adresse IP")
    parser.add_argument("-u", "--username", help="Recherche par username")
    args = parser.parse_args()

    if args.fullname:
        result = search_pages_jaunes(args.fullname)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    elif args.ipaddress:
        result = search_ip(args.ipaddress)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    elif args.username:
        asyncio.run(search_username_async(args.username))
    else:
        launch_gui()

if __name__ == "__main__":
    main()
