# -*- coding: utf-8 -*-
"""Guest portal copy — DE / EN / FR / IT / RM (Rumantsch)."""

from __future__ import annotations

LANGS = ("de", "en", "fr", "it", "rm")
LANG_LABELS = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "it": "Italiano",
    "rm": "Rumantsch",
}

TEXTS = {
    "de": {
        "title": "Hotel Anker",
        "headline": "Kostenloses WLAN",
        "lead": (
            "Gratis WLAN gegen Ihre E-Mail — für Infos zu Baufortschritt "
            "und Hotel Anker. Kein Spam, nur relevante Hotel- und Bau-Infos. "
            "Abmeldung jederzeit per Antwort an das Hotel."
        ),
        "email_label": "E-Mail-Adresse",
        "email_placeholder": "name@example.com",
        "consent": (
            "Ich willige ein, dass meine E-Mail gespeichert und für Infos zu "
            "Baufortschritt und Hotel Anker genutzt wird (Schweizer DSG)."
        ),
        "submit": "WLAN verbinden",
        "iphone_hint": (
            "iPhone: Für zuverlässige Wiedererkennung «Private WLAN-Adresse» "
            "für HotelAnkerGuest ausschalten (sonst neue Zufalls-MAC)."
        ),
        "success_title": "Verbunden — schönen Aufenthalt!",
        "success_body": "Bitte oben rechts auf Fertig tippen.",
        "error_email": "Bitte eine gültige E-Mail-Adresse eingeben.",
        "error_consent": "Bitte die Einwilligung bestätigen.",
        "error_mac": "Gerät nicht erkannt. Bitte WLAN neu verbinden und Captive Portal öffnen.",
        "error_auth": "Freischaltung fehlgeschlagen. Bitte erneut versuchen oder Rezeption fragen.",
        "lang_label": "Sprache",
    },
    "en": {
        "title": "Hotel Anker",
        "headline": "Free Wi‑Fi",
        "lead": (
            "Free Wi‑Fi in exchange for your email — for updates on construction "
            "progress and Hotel Anker. No spam, only relevant hotel and build news. "
            "Unsubscribe anytime by replying to the hotel."
        ),
        "email_label": "Email address",
        "email_placeholder": "name@example.com",
        "consent": (
            "I consent to my email being stored and used for construction and "
            "Hotel Anker updates (Swiss FADP)."
        ),
        "submit": "Connect Wi‑Fi",
        "iphone_hint": (
            "iPhone: For reliable recognition, turn off Private Wi‑Fi Address "
            "for HotelAnkerGuest (otherwise a new random MAC)."
        ),
        "success_title": "Connected — enjoy your stay!",
        "success_body": "Please tap Done in the top right.",
        "error_email": "Please enter a valid email address.",
        "error_consent": "Please confirm the consent checkbox.",
        "error_mac": "Device not recognised. Reconnect to Wi‑Fi and open the captive portal.",
        "error_auth": "Authorisation failed. Please try again or ask reception.",
        "lang_label": "Language",
    },
    "fr": {
        "title": "Hotel Anker",
        "headline": "Wi‑Fi gratuit",
        "lead": (
            "Wi‑Fi gratuit contre votre e-mail — pour des infos sur l’avancement "
            "des travaux et l’Hotel Anker. Pas de spam, uniquement des infos "
            "pertinentes. Désinscription à tout moment en répondant à l’hôtel."
        ),
        "email_label": "Adresse e-mail",
        "email_placeholder": "nom@exemple.com",
        "consent": (
            "J’accepte que mon e-mail soit enregistré et utilisé pour des infos "
            "sur le chantier et l’Hotel Anker (LPD suisse)."
        ),
        "submit": "Se connecter",
        "iphone_hint": (
            "iPhone : pour une reconnaissance fiable, désactivez l’adresse Wi‑Fi "
            "privée pour HotelAnkerGuest (sinon une nouvelle MAC aléatoire)."
        ),
        "success_title": "Connecté — bon séjour !",
        "success_body": "Veuillez toucher Terminé en haut à droite.",
        "error_email": "Veuillez saisir une adresse e-mail valide.",
        "error_consent": "Veuillez confirmer le consentement.",
        "error_mac": "Appareil non reconnu. Reconnectez-vous au Wi‑Fi et ouvrez le portail.",
        "error_auth": "Autorisation échouée. Réessayez ou demandez à la réception.",
        "lang_label": "Langue",
    },
    "it": {
        "title": "Hotel Anker",
        "headline": "Wi‑Fi gratuito",
        "lead": (
            "Wi‑Fi gratuito in cambio della vostra e-mail — per aggiornamenti "
            "sul cantiere e sull’Hotel Anker. Niente spam, solo informazioni "
            "rilevanti. Cancellazione in qualsiasi momento rispondendo all’hotel."
        ),
        "email_label": "Indirizzo e-mail",
        "email_placeholder": "nome@esempio.com",
        "consent": (
            "Acconsento alla memorizzazione e all’uso della mia e-mail per info "
            "su cantiere e Hotel Anker (LPD svizzera)."
        ),
        "submit": "Connetti Wi‑Fi",
        "iphone_hint": (
            "iPhone: per un riconoscimento affidabile, disattivate l’indirizzo "
            "Wi‑Fi privato per HotelAnkerGuest (altrimenti una nuova MAC casuale)."
        ),
        "success_title": "Connessi — buon soggiorno!",
        "success_body": "Toccate Fine in alto a destra.",
        "error_email": "Inserite un indirizzo e-mail valido.",
        "error_consent": "Confermate il consenso.",
        "error_mac": "Dispositivo non riconosciuto. Ricollegatevi al Wi‑Fi e aprite il portale.",
        "error_auth": "Autorizzazione non riuscita. Riprovate o chiedete alla reception.",
        "lang_label": "Lingua",
    },
    "rm": {
        "title": "Hotel Anker",
        "headline": "WLAN gratuit",
        "lead": (
            "WLAN gratuit cunter Vossa e-mail — per infos davart il progress da "
            "construcziun e l’Hotel Anker. Nagina spam, mo infos relevantas. "
            "Decancelaziun da tut temp cun responder a l’hotel."
        ),
        "email_label": "Adressa d’e-mail",
        "email_placeholder": "num@exempel.com",
        "consent": (
            "Jau consent che mia e-mail vegnia memorisada e duvrada per infos "
            "davart construcziun e Hotel Anker (LPD svizra)."
        ),
        "submit": "Connectar WLAN",
        "iphone_hint": (
            "iPhone: per ina renconuschientscha fidabla, deactivai l’adressa "
            "WLAN privata per HotelAnkerGuest (autramain ina nova MAC casuala)."
        ),
        "success_title": "Connectà — bun soggiorno!",
        "success_body": "Tutgai Finalisar sur engiu a dretga.",
        "error_email": "Endatai per plaschair ina e-mail valida.",
        "error_consent": "Confermai per plaschair il consentiment.",
        "error_mac": "Apparat betg renconuschì. Connectai danovamain e avri il portal.",
        "error_auth": "Autorisaziun fallida. Empruvai danovamain u dumondai a la recepziun.",
        "lang_label": "Lingua",
    },
}


def pick_lang(requested: str | None, accept_language: str | None) -> str:
    if requested:
        code = requested.strip().lower()[:2]
        if code in TEXTS:
            return code
    if accept_language:
        for part in accept_language.split(","):
            code = part.strip().split(";")[0].strip().lower()
            if code.startswith("rm"):
                return "rm"
            short = code[:2]
            if short in TEXTS:
                return short
    return "de"


def t(lang: str) -> dict:
    return TEXTS.get(lang) or TEXTS["de"]
