// Функція для валідації форми звіту


function validateFormReport() {
    const saleDate = document.getElementById('sale_date').value;
    const saleDateStg = document.getElementById('sale_date_stg').value;
    // Перевірка: чи заповнені поля
    if (!saleDate && !saleDateStg) {
        alert("Помилка: Будь ласка, вкажіть хоча б одну дату!");
        return false; // Блокує відправлення форми
    }
    const today = new Date();
    today.setHours(23, 59, 59, 0); // Встановлюємо час сьогоднішньої дати на кінець дня
    if (saleDate) {
        const selectedDate = new Date(saleDate);
        if (selectedDate > today) {
            alert("Помилка: Дата не може бути в майбутньому!");
            return false; // Блокує відправлення форми
        }
    }
    if (saleDateStg) {
        const selectedDateStg = new Date(saleDateStg);
        if (selectedDateStg > today) {
            alert("Помилка: Дата не може бути в майбутньому!");
            return false; // Блокує відправлення форми
        }
    }
    return true; // Дозволяє відправлення форми, якщо все ок
}
