/*
 Завдання на SQL до лекції 03.
 */


/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/
/* 1. Кількість фільмів у кожній категорії (за спаданням) */
SELECT
  c.name  AS category,
  COUNT(fc.film_id) AS film_count
FROM category c
JOIN film_category fc USING (category_id)
GROUP BY c.category_id, c.name
ORDER BY film_count DESC;

/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/
SELECT
  a.actor_id,
  a.first_name,
  a.last_name,
  COUNT(r.rental_id) AS rentals_count
FROM actor a
JOIN film_actor  fa USING (actor_id)
JOIN inventory   i  USING (film_id)
JOIN rental      r  USING (inventory_id)
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY rentals_count DESC
LIMIT 10;

/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/
SELECT
  c.name AS category,
  SUM(p.amount) AS total_revenue
FROM payment p
JOIN rental       r  USING (rental_id)
JOIN inventory    i  USING (inventory_id)
JOIN film_category fc USING (film_id)
JOIN category     c  USING (category_id)
GROUP BY c.category_id, c.name
ORDER BY total_revenue DESC
LIMIT 1;

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/
SELECT f.title
FROM film f
LEFT JOIN inventory i USING (film_id)
WHERE i.film_id IS NULL
ORDER BY f.title;

/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
SELECT
  a.actor_id,
  a.first_name,
  a.last_name,
  COUNT(*) AS films_in_children
FROM actor a
JOIN film_actor   fa USING (actor_id)
JOIN film_category fc USING (film_id)
JOIN category     c  USING (category_id)
WHERE c.name = 'Children'
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY films_in_children DESC, a.last_name, a.first_name
LIMIT 3;
