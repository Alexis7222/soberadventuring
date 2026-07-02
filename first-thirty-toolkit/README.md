# The First Thirty Sales Page

Static standalone sales page for the First Thirty PDF Toolkit.

## Files
- `index.html` - page structure and sales copy
- `styles.css` - responsive styling
- `script.js` - checkout link and price configuration
- `assets/` - workbook preview images exported from the PDF

## Checkout Setup
Open `script.js` and replace:

```js
checkoutUrl: "https://buy.stripe.com/4gMcN54YI11K8134Xy1ZS01",
price: "$17",
```

Use the public Stripe checkout URL for payment.

## Static Hosting
This page is published at `/first-thirty-toolkit/` in the `soberadventuring` repository.
