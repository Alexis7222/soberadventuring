const CONFIG = {
  price: "$17",
  checkoutUrl: "https://buy.stripe.com/4gMcN54YI11K8134Xy1ZS01",
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
