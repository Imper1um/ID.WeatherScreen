(() => {
    function formatTime(t) {
        let h = t.h % 12 || 12;
        let m = String(t.m).padStart(2, '0');
        let s = String(t.s).padStart(2, '0');
        let ampm = t.h >= 12 ? "pm" : "am";
        return `${h}:${m}:${s} ${ampm}`;
    }

    async function timeup() {
        try {
            const items = document.querySelectorAll(".timeup");
            items.forEach(el => {
                let [hours, minutes, seconds, ampm] = el.dataset.time.split(":");

                hours = parseInt(hours);
                minutes = parseInt(minutes);
                seconds = parseInt(seconds);
                ampm = ampm.toLowerCase();

                if (ampm === "pm" && hours < 12) hours += 12;
                if (ampm === "am" && hours === 12) hours = 0;

                let time = {
                    h: hours,
                    m: minutes,
                    s: seconds
                };

                time.s++;
                if (time.s >= 60) {
                    time.s = 0;
                    time.m++;
                    if (time.m >= 60) {
                        time.m = 0;
                        time.h = (time.h + 1) % 24;
                    }
                }
                if (time.h < 12) {
                    ampm = "am";
                } else {
                    ampm = "pm";
                }

                el.textContent = formatTime(time);
                el.dataset.time = `${time.h}:${time.m}:${time.s}:${ampm}`;
            });
        } catch (err) {
            console.error("Error updating timeup:", err);
        }
    }

    setInterval(timeup, 1000);
})();
