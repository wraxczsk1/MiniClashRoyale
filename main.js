// Jednoduchý „stav“ hry
let currentScreen = "menu"; // "menu" | "singleplayer" | "multiplayer" | "store"

const btnSingle = document.getElementById("btn-singleplayer");
const btnMulti = document.getElementById("btn-multiplayer");
const btnStore = document.getElementById("btn-store");

btnSingle.addEventListener("click", () => {
  currentScreen = "singleplayer";
  alert("Tady by se spustil Singleplayer mód Invertfronts.");
});

btnMulti.addEventListener("click", () => {
  currentScreen = "multiplayer";
  alert("Tady by se řešil Multiplayer (server browser, připojení, atd.).");
});

btnStore.addEventListener("click", () => {
  currentScreen = "store";
  alert("Tady by byl Store s kosmetikou a plášti.");
});

// Sem pak můžeš přidat canvas, WebGL, nebo cokoliv pro samotnou hru.
