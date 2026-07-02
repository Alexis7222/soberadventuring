const CONFIG = {
  price: "$17",
  checkoutUrl: "https://gumroad.com/l/drkgck",
};

document.addEventListener("DOMContentLoaded", () => {
  const price = document.querySelector("[data-price]");
  const buyButton = document.getElementById("buyButton");
  const year = document.getElementById("year");

  if (price) price.textContent = CONFIG.price;
  if (buyButton) buyButton.href = CONFIG.checkoutUrl;
  if (year) year.textContent = new Date().getFullYear();
});
