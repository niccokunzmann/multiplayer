- Wie würdest du gerne einen Konsolen-Chatclient schreiben?

Wenn ich einen Konsolen Chatclient schreibe, hätte ich gerne die Möglichkeit einfach auf einen Buffer zuzugreifen, in dem sich alle Nachrichten befinden, welche bisher gesendet wurden. Am besten mit access per index, damit ich mir aussuchen kann, welche Beiträge ich abfrage.
Für das versenden von Daten würde ich am liebsten am Anfang einmal eine Verbindung mit einem Server aufbauen (per IP) um dann mittels einer einfachen Funktion meine Nachricht zu senden.

- Wenn du schonmal ein Spiel geschrieben hast, wie stellst du dir Oberfläche und Programmcode vor, wenn das ein Multiplayerspiel wird.

Das hängt vom Spiel ab, aber im Prinzip ändert sich für den einzelnen Spieler für die meisten meiner Ideen nicht viel. Lediglich, das bestimmte Objekte von anderen Spielern kontrolliert werden ist anders als im Singleplayer modus. Die Verbindung sollte für den Spieler möglichst einfach sein, also am besten nur die Eingabe der IP erfordern.
Im Programmcode möchte ich möglichst gut Daten synchronisieren können. Dafür hätte ich am liebsten die Möglichkeit beliebige Objekte zu verschicken. Dann könnte ich ohne Probleme den kompletten Zustand oder nur wichtige Objekte synchronisieren. Diese Objekte sollten dann dem Empfänger in Form einer Liste zur Verfügung stehen.
Falls dabei die Daten zu viel Lag haben, wäre es gut, die Laufzeit jedes Paketes zu kennen um evtl. prediktiv zu arbeiten.


- Wie würdest du dich mit anderen Verbinden und Finden wollen? Wie sieht das aus? Bilder und oder Code. Wichtigstes zuerst. (Auch was sagen, das es noch garnicht gibt.)

Zur Verbindung möchte ich lediglich eine IP und einen Port angeben müssen. Zum annehmen dieser Verbindung soll der Server die Möglichkeit haben auf einem Port zuzuhören und dann alle neuen Verbindungen zu akzeptieren und in eine Liste zu packen. Jede Verbindung sollte eine Methode haben, die Daten an das entsprechende Gerät schickt. Außerdem sollte jede Verbindung eine Liste mit den bisher empfangenen Daten haben. 