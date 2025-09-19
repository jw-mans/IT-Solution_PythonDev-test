document.addEventListener('DOMContentLoaded', () => {
    const nextBtn = document.getElementById('next-quote');
    if (!nextBtn) return;

    async function updateQuoteCard(quoteData) {
        const card = document.querySelector('.quote-card');
        if (!card) return;

        card.querySelector('.quote-text').textContent = quoteData.text;
        card.querySelector('.quote-source').textContent = '— ' + quoteData.source;
        card.querySelector('.stat').textContent = '👁 ' + quoteData.views_cnt;
        card.querySelector('.like-count').textContent = quoteData.likes;
        card.querySelector('.dislike-count').textContent = quoteData.dislikes;

        card.querySelector('.like-form').dataset.id = quoteData.id;
        card.querySelector('.dislike-form').dataset.id = quoteData.id;

        const weightInput = card.querySelector('.weight-input');
        const weightIcon = card.querySelector('.weight-icon');
        const editBtn = card.querySelector('.edit-weight-btn');
        const saveBtn = card.querySelector('.save-weight-btn');
        const cancelBtn = card.querySelector('.cancel-weight-btn');
        const errorDiv = card.querySelector('.weight-error');

        const weight = parseFloat(quoteData.weight);
        const displayWeight = !isNaN(weight) ? weight.toFixed(2) : "0.00";

        if (weightInput) {
            weightInput.value = displayWeight;
            weightInput.defaultValue = displayWeight;
            weightInput.classList.add('hidden');
        }

        if (weightIcon) {
            weightIcon.textContent = `⚖ ${displayWeight}`;
            weightIcon.classList.remove('hidden');
        }

        if (editBtn) editBtn.classList.remove('hidden');
        if (saveBtn) saveBtn.classList.add('hidden');
        if (cancelBtn) cancelBtn.classList.add('hidden');

        if (errorDiv) {
            errorDiv.classList.add('hidden');
            errorDiv.textContent = '';
        }
    }

    nextBtn.addEventListener('click', async () => {
        nextBtn.disabled = true;

        try {
            const res = await fetch('/api/quote/random/');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const payload = await res.json();

            if (!payload.quote) {
                alert('Цитат пока нет 😢');
                return;
            }

            await updateQuoteCard(payload.quote);

        } catch (err) {
            console.error('Ошибка при получении случайной цитаты:', err);
            alert('Ошибка при получении цитаты. Смотри консоль разработчика.');
        } finally {
            nextBtn.disabled = false;
        }
    });
});
