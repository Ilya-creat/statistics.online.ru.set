$(document).ready(function () {
    let moskowUtc = 3;
    let timerId = setInterval(function () {
        let t = new Date(), tt = t.getUTCHours() + moskowUtc;
        alter(new Date().toLocaleString("en-US", {timeZone: "Europe/Moscow"}))
        document.getElementById('tik-tok').innerHTML = (tt > 24 || tt < 10 ? "0" : "") + (tt > 24 ? tt - 24 : tt) + ":" + (t.getMinutes() < 10 ? '0' : '') + t.getMinutes() + ":" + (t.getSeconds() < 10 ? '0' : '') + t.getSeconds();
        document.getElementById('tik-tok').classList.add("step");
    }, 1000);
});