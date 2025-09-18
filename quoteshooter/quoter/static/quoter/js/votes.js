/**
 * Анимация изменения счетчика лайков/дизлайков.
 *
 * @param {HTMLElement} el - элемент счетчика.
 * @param {number} newValue - новое значение счетчика.
 */
function animateCounter(el, newValue) {
    el.style.transition = "opacity 0.3s ease";
    el.style.opacity = 0;

    setTimeout(() => {
        el.textContent = newValue;
        el.style.opacity = 1;
    }, 300);
}

/**
 * Устанавливает обработчики голосования для всех форм.
 *
 * Логика:
 * 1. Определяет, является ли форма лайком или дизлайком.
 * 2. Отправляет POST-запрос на соответствующий URL.
 * 3. Обновляет счетчики лайков и дизлайков с анимацией.
 * 4. Подсвечивает активную кнопку (красная) и сбрасывает предыдущую.
 */
function setupVoteHandlers() {
    document.querySelectorAll(".like-form, .dislike-form").forEach(form => {
        form.addEventListener("submit", async e => {
            e.preventDefault();

            const quoteId = form.dataset.id;
            const isLike = form.classList.contains("like-form");
            const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;

            const url = isLike ? `/like/${quoteId}` : `/dislike/${quoteId}`;
            
            const res = await fetch(url, {
                method: "POST",
                headers: { "X-CSRFToken": csrf },
            });
            const data = await res.json();

            const likeCounter = document.querySelector(`.like-form[data-id='${quoteId}'] .like-count`);
            const dislikeCounter = document.querySelector(`.dislike-form[data-id='${quoteId}'] .dislike-count`);
            
            animateCounter(likeCounter, data.likes);
            animateCounter(dislikeCounter, data.dislikes);

            const likeBtn = document.querySelector(`.like-form[data-id='${quoteId}'] button`);
            const dislikeBtn = document.querySelector(`.dislike-form[data-id='${quoteId}'] button`);

            likeBtn.style.backgroundColor = "white";
            likeBtn.style.color = "#ff4e50";
            dislikeBtn.style.backgroundColor = "white";
            dislikeBtn.style.color = "#ff4e50";

            if (data.likes > 0 && isLike) {
                likeBtn.style.backgroundColor = "#ff4e50";
                likeBtn.style.color = "white";
            } else if (data.dislikes > 0 && !isLike) {
                dislikeBtn.style.backgroundColor = "#ff4e50";
                dislikeBtn.style.color = "white";
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupVoteHandlers();
});
