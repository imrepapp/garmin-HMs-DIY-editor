# HMs DIY szerkesztő

Böngészőben futó, telepítés nélküli tervező a Garmin **HMs DIY** Connect IQ adatmezőhöz
(szabadon építhető adatmező, szerző: hundsmiachn). Az eredeti Designer csak Windowson fut;
ez a szerkesztő ugyanazt az XML elrendezés-formátumot olvassa és írja.

## Használat

Nyisd meg az `index.html` fájlt egy böngészőben (egyetlen fájl, nincs build).

- **Hozzáadás**: érték, címke, vonal, keret, kör, ív, kitöltődő műszer-ív, folyamatsáv, grafikon, irányjelző.
- **Szerkesztés a képen**: húzás, fogókkal átméretezés, illesztés más elemekhez és a középvonalhoz,
  több elem kijelölése (Shift+kattintás vagy keret húzása).
- **Dinamikus színek**: az elem tulajdonságainál „Érték szerint változzon…” – a határokat valós
  mértékegységben adod meg, a ×10-es szorzást és a kulcsszínt a szerkesztő kezeli.
- **Előnézet**: 107 eszköz képernyőmérete és betűméretei, éjszakai mód, mintaértékek.
- **Mentés / megnyitás**: HMs DIY Designer XML (`<DIYLayout>`), a munka a böngészőben is megmarad.

## Ami még hiányzik

Az adatmező a beállításaiban egy kódolt „layout stringet” vár. Ennek a kódolása nincs
dokumentálva, ezért a szerkesztő egyelőre **nem** tudja előállítani: az itt mentett XML-t az eredeti
Designerben kell megnyitni (Load), majd *Copy to clipboard* → beillesztés a Garmin Connectben a
*Default layout string* mezőbe.

Egyéb ismert korlátok:

- A betűk képe közelítés (a Garmin nem adja ki a készülékek betűtípusait); a grafikus elemek helye pontos.
- Az értéktípusok kétbetűs kódjai a szerző példafájljaiból származnak. A `(?)` jelű megnevezések
  következtetések; a listában nem szereplő kódok megmaradnak, csak név nélkül látszanak.
- Új elrendezés mentésekor a fájl `ver="3.2.1" ifver="C"` Designer-verziót jelöl (a legfrissebb
  nyilvános példa szerint).

## Fejlesztés

Az eszköz- és betűtábla a Designer `fonts.txt` fájljából készül:

    python3 tools/gen_devices.py /path/to/fonts.txt

Forrás és példák: https://github.com/hundsmiachn/Garmin_HMsDIY
