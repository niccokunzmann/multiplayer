**Welche Fragen stellen sich dir, während du die folgenden beantwortest?**


**Wie würdest du gerne einen Konsolen-Chatclient schreiben?**

    from multiplayer import *
    console_connect_dialog()
    @everywhere
    def chat(username, words):
        print(username, ":", words)
    username = input("Your username:")
    while 1:
        text = input("> ")
        chat(username, text)
 
**Wenn du schonmal ein Spiel geschrieben hast, wie stellst du dir Oberfläche und Programmcode vor, wenn das ein Multiplayerspiel wird. (Die Änderungen bitte markieren. Kommentare sind auch gut. Verweise auf andere Spiele. Eigene Ideen.)**

Ich würde gerne alle objekte, die sich ändern können zwischen den Clients synchronisieren lassen.


**Wie hättest du gerne, dass ein LAN- oder Internet-Multiplayerspiel aussieht (Oberfläche, Programmcode)?**

Ein Verbinden Dialog für LAN. Cool auch, wenn man später noch ins Spiel einsteigen kann. Ich will auch Leuten einen Link schicken können. Dann lädt der das Spiel runter und startet es und wird gleich verbunden.
 
**Wie würdest du dich mit anderen Verbinden und Finden wollen? Wie sieht das aus? Bilder und oder Code. Wichtigstes zuerst. (Auch was sagen, das es noch garnicht gibt.)**

Ich sehe alle im LAN. Ich sehe alle, die im Internet Online sind und das Spiel gerade Hosten. Es gibt wie in SC2 einen Modus, in dem ich einfach nur sagen kann: ich will spielen und er findet andere Spieler.
 
**Beschreibe, wie ein oder mehrere Spiele funktionieren. Vom Starten des Spiels zum Spielen mit jemandem, zu GameOver, (Highscore), ... und bis zum Beenden des Spiels.**

Das Spiel startet. Ich sehe Multiplayer, Internet, LAN, Optionen, Single Player und gehe auf Multiplayer. Dann klicke ich auf neues Spiel. Der andere sieht dann das Spiel, weil er weiß wie es heißt oder weil er im LAN ist und steigt mit ein. Dann Spielen wir das.

Es gibt Phasen: Spiele finden und verbinden und Spielen.
Beim verbinden möchte ich sichere Datenstrukturen austauschen. 
Sowas wie Wer hostet es, wie verbinde ich mich. Ambesten so, dass man auch eigene Klassen mitschicken kann. Damit kann ich dann besseres Ranking machen, andere Spiele sehen. Teilnehmer, wenn ich mich verbinde und vorher schon.


**Welche Stellen im Code sind für andere/alle Spieler wichtig, welche nur für den vor dem Computer?**

Alle sollten den selben code haben. Es wäre cool, wenn z.B. alle den selben Canvas haben können und der synchronisiert wird. Jeder steuert seine Figuren. Es muss auch möglich sein, Pause zu machen. Aufgaben, die keinem gehören, müssen verlost werden. 