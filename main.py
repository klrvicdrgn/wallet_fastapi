from fastapi import FastAPI, Depends, HTTPException
from db import engine, db_dependency
from typing import Annotated
from helpers import get_conversion_rates
from models import Base, WalletCurrency
import auth
from helpers import get_current_user


app = FastAPI()
app.include_router(auth.router)

Base.metadata.create_all(bind=engine)
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/wallet")
async def wallet_status(user: user_dependency, db: db_dependency):
    currency_rates = get_conversion_rates()
    wallet = db.query(WalletCurrency).filter(WalletCurrency.user == user["id"])
    pln = wallet.filter(WalletCurrency.currency == "PLN").one_or_none()

    if wallet:
        wallet_converted = {
            f"{item.currency} in PLN": round(item.amount * currency_rates.get(item.currency), 2)
            for item in wallet if item.currency != "PLN"
        }
        if pln:
            wallet_converted['PLN'] = pln.amount
        wallet_converted['TOTAL PLN'] = round(sum(wallet_converted.values()), 2)
        return wallet_converted

    return wallet


@app.post("/wallet/add/{currency}/{amount}")
async def add_money(currency: str, amount: int, user: user_dependency, db: db_dependency):
    user_currency_amount = db.query(WalletCurrency).filter(
        WalletCurrency.user == user["id"], WalletCurrency.currency == currency.upper()).one_or_none()

    currency_rates = get_conversion_rates()
    if currency.upper() not in list(currency_rates.keys()) and currency.upper() != "PLN":
        raise HTTPException(status_code=404, detail="Currency NOT FOUND!")

    if user_currency_amount is None:
        create_user_currency_amount = WalletCurrency(
            user=user["id"],
            currency=currency,
            amount=amount
        )
        db.add(create_user_currency_amount)
        db.commit()
        return {create_user_currency_amount.currency: create_user_currency_amount.amount}
    else:
        user_currency_amount.amount += amount
        db.commit()
        return {user_currency_amount.currency: user_currency_amount.amount}


@app.post("/wallet/subtract/{currency}/{amount}")
async def subtract_money(currency: str, amount: int, user: user_dependency, db: db_dependency):
    user_currency_amount = db.query(WalletCurrency).filter(
        WalletCurrency.user == user["id"], WalletCurrency.currency == currency.upper()).one_or_none()

    if user_currency_amount is None:
        raise HTTPException(status_code=404, detail="Currency NOT FOUND!")
    else:
        if user_currency_amount.amount - amount < 0:
            raise HTTPException(status_code=404, detail=f"{amount} of {currency} NOT FOUND, you po'")
        else:
            user_currency_amount.amount -= amount
            db.commit()

    return {user_currency_amount.currency: user_currency_amount.amount}
