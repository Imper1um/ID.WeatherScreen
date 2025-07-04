(() => {
    const endpoint = "/api/current-data";

    async function updateDataItems() {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) return;

            const result = await response.json();

            const items = document.querySelectorAll(".data-item");
            items.forEach(el => {
                const key = el.dataset.item;
                const update = result[key];
                if (!update) return;

                if (update.content !== undefined) {
                    el.textContent = update.content;
                }

                if (update.data && Array.isArray(update.data)) {
                    update.data.forEach(attr => {
                        if (attr.key && attr.content !== undefined) {
                            el.setAttribute(attr.key, attr.content);
                        }
                    });
                }
            });
        } catch (err) {
            console.error("Error updating data items:", err);
        }
    }

    setInterval(updateDataItems, 60 * 1000);
})();
