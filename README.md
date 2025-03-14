# OS SETUP

## Install OS software
Start with update of packages on the machine (example below is for Debian based linux)

### Update the system
```bash
sudo apt update && sudo apt upgrade -yy && sudo apt autoremove
```

### Install packages
```bash
sudo apt install git docker docker-compose
```

## Start and enable docker service
```bash
sudo systemctl start docker.service
sudo systemctl enable docker.service
```

## To run docker without root access
> [!NOTE]
> Without this you will have to use sudo every time

```bash
sudo usermod -aG docker $USER
sudo reboot
```

# CLONE PROJECT

## Cloning with ssh using specific key
```bash
git clone git@github.com:klrvicdrgn/wallet_fastapi.git
```

## Create and populate .env
After cloning the project, variables from .env.dist should be copied and populated in the .env file

> [!NOTE]
> ALGORITHM can be say HS256, SECRET_KEY more less any string, but it is recommended to use random set of say 50 chars

# RUN SERVER LOCALLY

## Build docker image
Navigate to the location of the cloned project and run the following command

```bash
docker compose up --build
```

> [!NOTE]
> If there is an issue with network while running the command do the following

```bash
sudo systemctl restart NetworkManager
sudo service docker restart
```

> [!NOTE]
> Another issue with network can be due to VPN, please disable it for running project locally

After the server is started successfully, you can test the endpoints functionalities on the follwing link http://127.0.0.1:8000/docs


# USAGE

## Creating user
User HAS TO BE created on /auth in order to use the app.
After user is created, login needs to happen in order to use the endpoints (authorize button to authorize the access to the endpoints). Expiry is in 20 minutes, after which user needs to be logged in again.

> [!NOTE]
> ALL endpoints are protected and user needs to be logged in to use them.

## Checking wallet
Wallet can be seen on /wallet after login. 

## Adding funds to wallet
Funds can be added to wallet via /wallet/add/{currency}/{amount}
If new currency is added, a new DB entry will be created for the current user and chosen currency and amount.
If currency does not exist on API used for conversion rates, the error will be raised.
If currency is PLN it will be added though it does not exist on API, but this is simply considered to be 1:1 rate, as the task request is that every currency is shown in PLN.
If currency already exist in the DB for current user, amount will be increased for the chosen amount.

## Removing funds from wallet
Funds can be removed via /wallet/subtract/{currency}/{amount}
If chosen currency does not exist error will be raised.
If amount is greater than the amount available error will be raised.
Funds will be subtracted from the current amount for chosen currency and currently logged in user.