import stripe

def create_customer(email):
    customer = stripe.Customer.create(email=email)
    return customer.id