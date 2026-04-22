# KTH Bot - Automatisk TimeEdit-bekräftelse

En smidig Python-applikation som körs i bakgrunden och automatiskt bekräftar dina rumsbokningar på KTH (via TimeEdit). Boten sköter inloggningen och ser till att du inte tappar dina bokade tider.

## Funktioner
- **Automatisk bekräftelse:** Boten kollar och bekräftar bokningar var 10:e minut.
- **Körs i bakgrunden:** Appen minimeras till systemfältet (system tray) så att den inte stör ditt arbete.
- **Enkel konfiguration:** Ange dina inloggningsuppgifter direkt i appen vid start.

## Installation

Följ dessa steg för att komma igång:

### 0. Installera Python
Om du inte redan har Python installerat, ladda ner och installera det här:
[Ladda ner Python](https://www.python.org/ftp/python/pymanager/python-manager-26.1.msix)

### 1. Installera bibliotek
Öppna terminalen (cmd) och kör följande kommando för att installera de nödvändiga paketen:
```bash
pip install playwright pystray Pillow
```

### 2. Installera Playwright Browser
Boten använder Chromium för att navigera på webben. Installera det genom att köra:
```bash
python -m playwright install chromium
```

## Användning

1. **Namnge filen:** Se till att din fil heter `kth-bot.pyw`. (Ändelsen `.pyw` gör att programmet kan köras utan att ett svart kommandofönster syns i bakgrunden).
2. **Starta boten:** Dubbelklicka på `kth-bot.pyw`.
3. **Logga in:** Ange din KTH-mejl och ditt lösenord i fönstren som dyker upp.
4. **Klart!** Boten ligger nu nere vid klockan i aktivitetsfältet och jobbar.

## Hur det fungerar
- När du startar programmet valideras dina uppgifter mot KTH:s inloggningssida.
- Om inloggningen lyckas startas en loop som var 10:e minut besöker TimeEdit för att trycka på "Bekräfta"-knappen om en bokning är aktiv.
- Du kan när som helst visa loggen eller avsluta programmet genom att högerklicka på ikonen i systemfältet.

---
*Disclaimer: Denna bot är ett hjälpmedel. Se till att följa KTH:s regler för rumsbokning.*