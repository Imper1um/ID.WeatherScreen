(() => {
    const localTimeEl = document.getElementById("localtime");
    const uptimeEl = document.getElementById("uptime");

    if (!localTimeEl || !uptimeEl) return;

    let [hours, minutes, seconds, ampm] = localTimeEl.dataset.time.split(":");
    let totalUptimeSeconds = parseInt(uptimeEl.dataset.uptime, 10) || 0;

    hours = parseInt(hours);
    minutes = parseInt(minutes);
    seconds = parseInt(seconds);
    ampm = ampm.toLowerCase();

    if (ampm === "pm" && hours < 12) hours += 12;
    if (ampm === "am" && hours === 12) hours = 0;

    let localTime = {
        h: hours,
        m: minutes,
        s: seconds
    };

    function formatLocalTime(t) {
        let h = t.h % 12 || 12;
        let m = String(t.m).padStart(2, '0');
        let s = String(t.s).padStart(2, '0');
        let ampm = t.h >= 12 ? "pm" : "am";
        return `${h}:${m}:${s} ${ampm}`;
    }

    function formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hrs = Math.floor((seconds % 86400) / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        const parts = [];
        if (days > 0) parts.push(`${days}d`);
        if (hrs > 0 || days > 0) parts.push(`${hrs}h`);
        if (mins > 0 || hrs > 0 || days > 0) parts.push(`${mins}m`);
        parts.push(`${secs}s`);
        return parts.join(" ");
    }

    function tick() {
        localTime.s++;
        if (localTime.s >= 60) {
            localTime.s = 0;
            localTime.m++;
            if (localTime.m >= 60) {
                localTime.m = 0;
                localTime.h = (localTime.h + 1) % 24;
            }
        }

        totalUptimeSeconds++;

        localTimeEl.textContent = formatLocalTime(localTime);
        uptimeEl.textContent = formatUptime(totalUptimeSeconds);
    }

    localTimeEl.textContent = formatLocalTime(localTime);
    uptimeEl.textContent = formatUptime(totalUptimeSeconds);

    setInterval(tick, 1000);
})();
