(() => {
    function formatUptick(seconds) {
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

    async function tickup() {
        try {
            const items = document.querySelectorAll(".tickup");
            items.forEach(el => {
                let s = el.dataset.seconds;
                s++;
                el.dataset.seconds = s;

                let display = formatUptick(s);
                el.textContent = display;
            });
        } catch (err) {
            console.error("Error updating data items:", err)
        }
    }

    setInterval(tickup, 1000);
})();