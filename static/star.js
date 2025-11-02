const starsContainer = document.getElementById("stars");
const ratingInput = document.getElementById("rating");

for (let i = 1; i <= 5; i++) {
    const star = document.createElement("span");
    star.textContent = "☆";
    star.dataset.value = i;
    star.style.cursor = "pointer";
    star.onclick = () => {
        ratingInput.value = i;
        updateStars(i);
    };
    starsContainer.appendChild(star);
}

function updateStars(value) {
    starsContainer.querySelectorAll("span").forEach(star => {
        star.textContent = star.dataset.value <= value ? "★" : "☆";
    });
}
