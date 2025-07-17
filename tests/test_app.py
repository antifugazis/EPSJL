import pytest
from playwright.sync_api import sync_playwright

# Adjust this URL if your Flask app runs on a different port
BASE_URL = "http://localhost:5000/"

def test_homepage_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        assert page.title() != ""
        assert "Connexion" in page.content() or "Accueil" in page.content()
        browser.close()

def test_login_page_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL + "login")
        assert "Connexion" in page.content() or "Login" in page.content()
        browser.close()

def test_finances_page_requires_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL + "finances/")
        # Should redirect to login if not authenticated
        assert "Connexion" in page.content() or "Login" in page.content()
        browser.close()
