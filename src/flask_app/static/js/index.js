// Функція для валідації форми звіту


function validateFormReport() {
    const saleDate = document.getElementById('sale_date').value;
    const saleDateStg = document.getElementById('sale_date_stg').value;
    // Перевірка: чи заповнені поля
    if (!saleDate && !saleDateStg) {
        alert("Помилка: Будь ласка, вкажіть хоча б одну дату!");
        return false; // Блокує відправлення форми
    }
    if (saleDate) {
        const selectedDate = new Date(saleDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Встановлюємо час сьогоднішньої дати на початок дня
        if (selectedDate > today) {
            alert("Помилка: Дата не може бути в майбутньому!");
            return false; // Блокує відправлення форми
        }
    }
    if (saleDateStg) {
        const selectedDateStg = new Date(saleDateStg);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Встановлюємо час сьогоднішньої дати на початок дня
        if (selectedDateStg > today) {
            alert("Помилка: Дата не може бути в майбутньому!");
            return false; // Блокує відправлення форми
        }
    }
    return true; // Дозволяє відправлення форми, якщо все ок
}
