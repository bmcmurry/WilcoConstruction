document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".search-form");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const searchField = formData.get("search_field");
      const searchQuery = formData.get("search_query");
      const rentalCardsContainer = document.getElementById("rental-cards-container");
      const rentalCards = rentalCardsContainer.querySelectorAll(".rental-card");

      rentalCards.forEach(function (card) {
        const fieldData = card.getAttribute("data-" + searchField);
        if (fieldData.toLowerCase().includes(searchQuery.toLowerCase())) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
    });
  });