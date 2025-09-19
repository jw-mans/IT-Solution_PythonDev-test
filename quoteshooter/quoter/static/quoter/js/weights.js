function setupWeightHandlers(card) {
    const weightInput = card.querySelector('.weight-input');
    const weightIcon = card.querySelector('.weight-icon');
    const editBtn = card.querySelector('.edit-weight-btn');
    const saveBtn = card.querySelector('.save-weight-btn');
    const cancelBtn = card.querySelector('.cancel-weight-btn');
    const errorDiv = card.querySelector('.weight-error');

    if (!weightInput || !weightIcon || !editBtn || !saveBtn || !cancelBtn) return;

    // Сбрасываем вид кнопок и input
    weightInput.classList.add('hidden');
    weightIcon.classList.remove('hidden');
    editBtn.classList.remove('hidden');
    saveBtn.classList.add('hidden');
    cancelBtn.classList.add('hidden');
    errorDiv.classList.add('hidden');

    // Удаляем старые обработчики (если есть)
    editBtn.onclick = null;
    saveBtn.onclick = null;
    cancelBtn.onclick = null;

    // Привязываем новые
    editBtn.addEventListener('click', () => {
        weightInput.classList.remove('hidden');
        weightIcon.classList.add('hidden');
        editBtn.classList.add('hidden');
        saveBtn.classList.remove('hidden');
        cancelBtn.classList.remove('hidden');
    });

    cancelBtn.addEventListener('click', () => {
        weightInput.value = weightInput.defaultValue;
        weightInput.classList.add('hidden');
        weightIcon.classList.remove('hidden');
        editBtn.classList.remove('hidden');
        saveBtn.classList.add('hidden');
        cancelBtn.classList.add('hidden');
        errorDiv.classList.add('hidden');
    });

    saveBtn.addEventListener('click', async () => {
        const newWeight = parseFloat(weightInput.value);
        if (isNaN(newWeight) || newWeight < 0 || newWeight > 100) {
            errorDiv.textContent = 'Вес должен быть от 0 до 100.';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            const res = await fetch(`/quotes/${card.dataset.id}/update_weight/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ weight: newWeight })
            });
            const data = await res.json();
            if (data.success) {
                weightInput.defaultValue = newWeight.toFixed(2);
                weightInput.classList.add('hidden');
                weightIcon.textContent = `⚖ ${newWeight.toFixed(2)}`;
                weightIcon.classList.remove('hidden');
                editBtn.classList.remove('hidden');
                saveBtn.classList.add('hidden');
                cancelBtn.classList.add('hidden');
                errorDiv.classList.add('hidden');
            } else {
                errorDiv.textContent = data.error || 'Ошибка при обновлении веса';
                errorDiv.classList.remove('hidden');
            }
        } catch (err) {
            console.error(err);
            errorDiv.textContent = 'Ошибка на сервере';
            errorDiv.classList.remove('hidden');
        }
    });
}

// Инициализация для всех карточек на странице
document.querySelectorAll('.quote-card').forEach(card => setupWeightHandlers(card));
