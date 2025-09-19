document.addEventListener('DOMContentLoaded', () => {
    const nextBtn = document.getElementById('next-quote');
    if (!nextBtn) return;

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

            const q = payload.quote;
            const card = document.querySelector('.quote-card');
            if (!card) throw new Error('Карточка цитаты не найдена в DOM');

            const textEl = card.querySelector('.quote-text');
            const sourceEl = card.querySelector('.quote-source');
            const statEl = card.querySelector('.stat');
            const likeCountEl = card.querySelector('.like-count');
            const dislikeCountEl = card.querySelector('.dislike-count');
            const likeForm = card.querySelector('.like-form');
            const dislikeForm = card.querySelector('.dislike-form');

            if (textEl) textEl.textContent = q.text;
            if (sourceEl) sourceEl.textContent = '— ' + q.source;
            if (statEl) statEl.textContent = '👁 ' + q.views_cnt;
            if (likeCountEl) likeCountEl.textContent = q.likes;
            if (dislikeCountEl) dislikeCountEl.textContent = q.dislikes;
            if (likeForm) likeForm.setAttribute('data-id', q.id);
            if (dislikeForm) dislikeForm.setAttribute('data-id', q.id);
        } catch (err) {
            console.error('Ошибка при получении случайной цитаты:', err);
            alert('Ошибка при получении цитаты. Смотри консоль разработчика.');
        } finally {
            nextBtn.disabled = false;
        }
    });
});
