const CONFIG = {
  price: "$17",
  checkoutUrl: "https://gumroad.com/l/drkgck",
};

document.addEventListener("DOMContentLoaded", () => {
  const prices = document.querySelectorAll("[data-price]");
  const buyButtons = document.querySelectorAll("#buyButton, #buyButtonTop");

  prices.forEach((price) => {
    price.textContent = CONFIG.price;
  });

  buyButtons.forEach((button) => {
    button.href = CONFIG.checkoutUrl;
  });
});
