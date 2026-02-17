from afrogeo import verify

# Full mode
r1 = verify({
    "country": "Nigeria",
    "state": "Lagos",
    "city": "Ikeja",
    "lga": "Ojodu"
})
print(r1, r1.normalized)

# Minimal mode
r2 = verify({
    "country": "Nigeria",
    "state": "Lagos",
    "lga": "Ojodu"
})
print(r2, r2.normalized)

# Wrong input
r3 = verify({
    "country": "Nigeria",
    "state": "Lagos",
    "lga": "InvalidLGA"
})
print(r3, r3.normalized)
