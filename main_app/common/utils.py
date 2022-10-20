import requests
import json
import os
from datetime import datetime as dt
import time
import pytz as pytz
from dateutil.tz import tzlocal
from dotenv import load_dotenv
from atm_functions.models import Account, Balance, DigitalCurrency
from atm_functions.models import User
from .cryptoapis import CryptoApis
import random
import string

load_dotenv()


def get_user_count():
    return User.objects.all().count(), dt.now().astimezone(pytz.timezone('US/Eastern')).strftime("%D")
    #return Account.objects.count(), dt.now().astimezone('localtimezone').strftime("%D %r %Z")  

def generate_pin():
    return ''.join(random.choice(string.digits) for i in range(6))

def get_currencies_exchange_rate():
    cryptoapis_client = CryptoApis()

    exchange_rate_ltc = cryptoapis_client.get_exchange_rate_by_symbols("LTC", "USD")["rate"]
    rate_ltc = {
        "currency_name": "Litecoin",
        "symbol": "LTC",
        "exchange_rate": round(float(exchange_rate_ltc), 2)
    }

    exchange_rate_bch = cryptoapis_client.get_exchange_rate_by_symbols("BCH", "USD")["rate"]
    rate_bch = {
        "currency_name": "Bitcoin Cash",
        "symbol": "BCH",
        "exchange_rate": round(float(exchange_rate_bch), 2)
    }

    exchange_rate_dash = cryptoapis_client.get_exchange_rate_by_symbols("DASH", "USD")["rate"]
    rate_dash = {
        "currency_name": "Dash",
        "symbol": "DASH",
        "exchange_rate": round(float(exchange_rate_dash), 2)
    }

    exchange_rate_zec = cryptoapis_client.get_exchange_rate_by_symbols("ZEC", "USD")["rate"]
    rate_zec = {
        "currency_name": "Zcash",
        "symbol": "ZEC",
        "exchange_rate": round(float(exchange_rate_zec), 2)
    }

    exchange_rate_xrp = cryptoapis_client.get_exchange_rate_by_symbols("XRP", "USD")["rate"]
    rate_xrp = {
        "currency_name": "XRP",
        "symbol": "XRP",
        "exchange_rate": round(float(exchange_rate_xrp), 2)
    }

    exchange_rates = []
    exchange_rates.append(rate_ltc)
    exchange_rates.append(rate_bch)
    exchange_rates.append(rate_dash)
    exchange_rates.append(rate_zec)
    exchange_rates.append(rate_xrp)

    return exchange_rates

def calculate_credit_grade(user):

    balances = Balance.objects.filter(email = user, currency_name__currency_type="SAVINGS")
    user = Account.objects.get(user = user)

    total_usd_balance = 0

    for balance in balances:
        currency = balance.currency_name

        currency_usd_balance = balance.amount * currency.exchange_rate
        total_usd_balance += currency_usd_balance

    cryptoshare_credits_object = DigitalCurrency.objects.get(symbol="CSC")
    credits_balance = Balance.objects.get(email = user.user, digital_currency_name = cryptoshare_credits_object)

    total_usd_balance += credits_balance.amount * cryptoshare_credits_object.exchange_rate

    credit_grades = {
                    "FFF": {
                            "lower_limit": 0,
                            "upper_limit": 99
                            },
                    "FF": {
                            "lower_limit": 100,
                            "upper_limit": 599
                            },
                    "F": {
                            "lower_limit": 600,
                            "upper_limit": 999
                            },
                    "E": {
                            "lower_limit": 1000,
                            "upper_limit": 9999
                            },
                    "D": {
                            "lower_limit": 10000,
                            "upper_limit": 59999
                            },
                    "C": {
                            "lower_limit": 60000,
                            "upper_limit": 99999
                            },
                    "B": {
                            "lower_limit": 100000,
                            "upper_limit": 599999
                            },
                    "A": {
                            "lower_limit": 600000,
                            "upper_limit": 999999
                            },
                    "AA": {
                            "lower_limit": 1000000,
                            "upper_limit": 9999999
                            },
                    "AAA": {
                            "lower_limit": 10000000,
                            "upper_limit": None
                            }

                }

    for credit_grade in credit_grades:
        if credit_grades[credit_grade]["upper_limit"] is None:
            user.credit_grade = credit_grade
            user.save()
            break

        if total_usd_balance <= credit_grades[credit_grade]["upper_limit"]:
            user.credit_grade = credit_grade
            user.save()
            break

swap_crypto_info = {
    "BTC": {
        "symbol": "btc",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Bitcoin",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^[13][a-km-zA-HJ-NP-Z1-9]{25,80}$|^(bc1)[0-9A-Za-z]{25,80}$",
        "validation_extra": None,
        "address_explorer": "https://blockchair.com/bitcoin/address/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/bitcoin/transaction/{}?from=simpleswap",
        "confirmations_from": "1",
        "image": "/static/img/currencies/btc.svg"
    },
    "ETH": {
        "symbol": "eth",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Ethereum",
        "warnings_from": [
            "Please be careful not to deposit your ETH from a smart contract."
        ],
        "warnings_to": [
            "Please be careful not to provide a smart contract as your ETH payout address."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "1",
        "image": "/static/img/currencies/eth.svg"
    },
    "LTC": {
        "symbol": "ltc",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Litecoin",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^(L|M|3)[A-Za-z0-9]{33}$|^(ltc1)[0-9A-Za-z]{39}$",
        "validation_extra": None,
        "address_explorer": "https://blockchair.com/litecoin/address/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/litecoin/transaction/{}?from=simpleswap",
        "confirmations_from": "1",
        "image": "/static/img/currencies/ltc.svg"
    },
    "BCH": {
        "symbol": "bch",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Bitcoin Cash",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^([13][a-km-zA-HJ-NP-Z1-9]{25,34})$|^((bitcoincash:)?(q|p)[a-z0-9]{41})$|^((BITCOINCASH:)?(Q|P)[A-Z0-9]{41})$",
        "validation_extra": None,
        "address_explorer": "https://blockchair.com/bitcoin-cash/address/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/bitcoin-cash/transaction/{}?from=simpleswap",
        "confirmations_from": "2",
        "image": "/static/img/currencies/bch.svg"
    },
    "ZEC":{
        "symbol": "zec",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Zcash",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^(t)[A-Za-z0-9]{34}$",
        "validation_extra": None,
        "address_explorer": "https://explorer.zcha.in/accounts/{}",
        "tx_explorer": "https://explorer.zcha.in/transactions/{}",
        "confirmations_from": "12",
        "image": "/static/img/currencies/zec.svg"
    },
    "XRP": {
        "symbol": "xrp",
        "network": "",
        "has_extra_id": True,
        "extra_id": "Destination tag",
        "name": "XRP",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^r[1-9A-HJ-NP-Za-km-z]{25,34}$",
        "validation_extra": "^([0-9]{1,19})$",
        "address_explorer": "https://blockchair.com/ripple/account/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/ripple/transaction/{}?from=simpleswap",
        "confirmations_from": "10",
        "image": "/static/img/currencies/xrp.svg"
    },
    "DASH": {
        "symbol": "dash",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Dash",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^[X|7][0-9A-Za-z]{33}$",
        "validation_extra": None,
        "address_explorer": "https://blockchair.com/dash/address/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/dash/transaction/{}?from=simpleswap",
        "confirmations_from": "10",
        "image": "/static/img/currencies/dash.svg"
    },
    "DOGE": {
        "symbol": "doge",
        "network": "",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Dogecoin",
        "warnings_from": [],
        "warnings_to": [],
        "validation_address": "^(D|A|9)[a-km-zA-HJ-NP-Z1-9]{33,34}$",
        "validation_extra": None,
        "address_explorer": "https://blockchair.com/dogecoin/address/{}?from=simpleswap",
        "tx_explorer": "https://blockchair.com/dogecoin/transaction/{}?from=simpleswap",
        "confirmations_from": "6",
        "image": "/static/img/currencies/doge.svg"
    },
    "LINK": {
        "symbol": "link",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Chainlink",
        "warnings_from": [
            "Please note that only LINK ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only LINK ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/link.svg"
    },
    "SHIB": {
        "symbol": "shib",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "SHIBA INU",
        "warnings_from": [
            "Please note that only SHIB ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only SHIB ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/S.svg"
    },
    "BAT": {
        "symbol": "bat",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Basic Attention Token",
        "warnings_from": [
            "Please note that only BAT ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only BAT ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/bat.svg"
    },
    "USDC": {
        "symbol": "usdc",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "USD Coin",
        "warnings_from": [
            "Please note that only USDC ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only USDC ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/U.svg"
    },
    "USDTERC20": {
        "symbol": "usdterc20",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "825",
        "name": "Tether ERC20",
        "warnings_from": [
            "Please note that only USDT ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only USDT ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/T.svg"
    },
    "WBTC": {
        "symbol": "wbtc",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Wrapped Bitcoin",
        "warnings_from": [
            "Please note that only WBTC ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only WBTC ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/W.svg"
    },
    "MKR": {
        "symbol": "mkr",
        "network": "ERC20",
        "has_extra_id": False,
        "extra_id": "",
        "name": "Maker",
        "warnings_from": [
            "Please note that only MKR ERC-20 tokens are available for the deposit."
        ],
        "warnings_to": [
            "Please note that only MKR ERC-20 tokens are available for the withdrawal."
        ],
        "validation_address": "^(0x)[0-9A-Fa-f]{40}$",
        "validation_extra": None,
        "address_explorer": "https://etherscan.io/address/{}",
        "tx_explorer": "https://etherscan.io/tx/{}",
        "confirmations_from": "24",
        "image": "/static/img/currencies/mkr.svg"
    },
}

countries_dict = {
    "AF": "Afghanistan",
    "AX": "Aland Islands",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BB": "Barbados",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "CV": "Cape Verde",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia",
    "KM": "Comoros",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "CW": "Curacao",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (Malvinas)",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and Mcdonald Islands",
    "VA": "Holy See (Vatican City State)",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KR": "Korea, Republic of",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic",
    "LV": "Latvia",
    "LS": "Lesotho",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia, Federated States of",
    "MD": "Moldova, Republic of",
    "MC": "Monaco",
    "MN": "Mongolia",
    "MS": "Montserrat",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NR": "Nauru",
    "NL": "Netherlands",
    "AN": "Netherlands Antilles",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestinian Territory, Occupied",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "RE": "Reunion",
    "RU": "Russian Federation",
    "RW": "Rwanda",
    "BL": "Saint Barthelemy",
    "SH": "Saint Helena",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten",
    "SK": "Slovakia",
    "SB": "Solomon Islands",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SZ": "Swaziland",
    "SE": "Sweden",
    "CH": "Switzerland",
    "TW": "Taiwan, Province of China",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States",
    "US2": "United States Minor Outlying Islands",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Viet Nam",
    "VG": "Virgin Islands, British",
    "US3": "Virgin Islands, U.S.",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia"
}

countries_tuples = [ (k, v) for k, v in countries_dict.items() ]

banned_countries = {
    "AF": {
        "name": "Afghanistan",
        "code": "AF"
    },
    "BA": {
        "name": "Balkans",
        "code": "BA"
    },
    "BD": {
        "name": "Bangladesh",
        "code": "BD"
    },
    "BO": {
        "name": "Bolivia",
        "code": "BO"
    },
    "BY": {
        "name": "Belarus",
        "code": "BY"
    },
    "CD": {
        "name": "Democratic Republic of the Congo",
        "code": "CD"
    },
    "CI": {
        "name": "Cote d'Ivoire",
        "code": "CI"
    },
    "CN": {
        "name": "China",
        "code": "CN"
    },
    "CU": {
        "name": "Cuba",
        "code": "CU"
    },
    "DZ": {
        "name": "Algeria",
        "code": "DZ"
    },
    "EG": {
        "name": "Egypt",
        "code": "EG"
    },
    "ER": {
        "name": "Eritrea",
        "code": "ER"
    },
    "ID": {
        "name": "Indonesia",
        "code": "ID"
    },
    "IQ": {
        "name": "Iraq",
        "code": "IQ"
    },
    "IR": {
        "name": "Iran",
        "code": "IR"
    },
    "KH": {
        "name": "Cambodia",
        "code": "KH"
    },
    "KP": {
        "name": "North Korea",
        "code": "KP"
    },
    "LA": {
        "name": "Laos",
        "code": "LA"
    },
    "LR": {
        "name": "Liberia",
        "code": "LR"
    },
    "MA": {
        "name": "Morocco",
        "code": "MA"
    },
    "MK": {
        "name": "North Macedonia",
        "code": "MK"
    },
    "MM": {
        "name": "Burma",
        "code": "MM"
    },
    "NP": {
        "name": "Nepal",
        "code": "NP"
    },
    "QA": {
        "name": "Qatar",
        "code": "QA"
    },
    "RU": {
        "name": "Russia",
        "code": "RU"
    },
    "SD": {
        "name": "Sudan",
        "code": "SD"
    },
    "SY": {
        "name": "Syria",
        "code": "SY"
    },
    "TN": {
        "name": "Tunisia",
        "code": "TN"
    },
    "UA": {
        "name": "Sevastopol",
        "code": "UA"
    },
    "VE": {
        "name": "Venezuela",
        "code": "VE"
    },
    "ZW": {
        "name": "Zimbabwe",
        "code": "ZW"
    }
}

"""
country_dict = {
    'US': "United States",
    'BR': "Brazil",
    'CL': "Chile",
    'CO': "Colombia",
    'EC': "Ecuador",
    'PE': "Peru",
    'UY': "Uruguay"
}

state_dict = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

"""
# currency_list = ['USD', 'COL', 'BRL']

"""
country_codes = [{
"name": "Afghanistan",
"dial_code": "+93",
"code": "AF"
},
{
"name": "Aland Islands",
"dial_code": "+358",
"code": "AX"
},
{
"name": "Albania",
"dial_code": "+355",
"code": "AL"
},
{
"name": "Algeria",
"dial_code": "+213",
"code": "DZ"
},
{
"name": "AmericanSamoa",
"dial_code": "+1684",
"code": "AS"
},
{
"name": "Andorra",
"dial_code": "+376",
"code": "AD"
},
{
"name": "Angola",
"dial_code": "+244",
"code": "AO"
},
{
"name": "Anguilla",
"dial_code": "+1264",
"code": "AI"
},
{
"name": "Antarctica",
"dial_code": "+672",
"code": "AQ"
},
{
"name": "Antigua and Barbuda",
"dial_code": "+1268",
"code": "AG"
},
{
"name": "Argentina",
"dial_code": "+54",
"code": "AR"
},
{
"name": "Armenia",
"dial_code": "+374",
"code": "AM"
},
{
"name": "Aruba",
"dial_code": "+297",
"code": "AW"
},
{
"name": "Australia",
"dial_code": "+61",
"code": "AU"
},
{
"name": "Austria",
"dial_code": "+43",
"code": "AT"
},
{
"name": "Azerbaijan",
"dial_code": "+994",
"code": "AZ"
},
{
"name": "Bahamas",
"dial_code": "+1242",
"code": "BS"
},
{
"name": "Bahrain",
"dial_code": "+973",
"code": "BH"
},
{
"name": "Bangladesh",
"dial_code": "+880",
"code": "BD"
},
{
"name": "Barbados",
"dial_code": "+1246",
"code": "BB"
},
{
"name": "Belarus",
"dial_code": "+375",
"code": "BY"
},
{
"name": "Belgium",
"dial_code": "+32",
"code": "BE"
},
{
"name": "Belize",
"dial_code": "+501",
"code": "BZ"
},
{
"name": "Benin",
"dial_code": "+229",
"code": "BJ"
},
{
"name": "Bermuda",
"dial_code": "+1441",
"code": "BM"
},
{
"name": "Bhutan",
"dial_code": "+975",
"code": "BT"
},
{
"name": "Bolivia, Plurinational State of",
"dial_code": "+591",
"code": "BO"
},
{
"name": "Bosnia and Herzegovina",
"dial_code": "+387",
"code": "BA"
},
{
"name": "Botswana",
"dial_code": "+267",
"code": "BW"
},
{
"name": "Brazil",
"dial_code": "+55",
"code": "BR"
},
{
"name": "British Indian Ocean Territory",
"dial_code": "+246",
"code": "IO"
},
{
"name": "Brunei Darussalam",
"dial_code": "+673",
"code": "BN"
},
{
"name": "Bulgaria",
"dial_code": "+359",
"code": "BG"
},
{
"name": "Burkina Faso",
"dial_code": "+226",
"code": "BF"
},
{
"name": "Burundi",
"dial_code": "+257",
"code": "BI"
},
{
"name": "Cambodia",
"dial_code": "+855",
"code": "KH"
},
{
"name": "Cameroon",
"dial_code": "+237",
"code": "CM"
},
{
"name": "Canada",
"dial_code": "+1",
"code": "CA"
},
{
"name": "Cape Verde",
"dial_code": "+238",
"code": "CV"
},
{
"name": "Cayman Islands",
"dial_code": "+ 345",
"code": "KY"
},
{
"name": "Central African Republic",
"dial_code": "+236",
"code": "CF"
},
{
"name": "Chad",
"dial_code": "+235",
"code": "TD"
},
{
"name": "Chile",
"dial_code": "+56",
"code": "CL"
},
{
"name": "China",
"dial_code": "+86",
"code": "CN"
},
{
"name": "Christmas Island",
"dial_code": "+61",
"code": "CX"
},
{
"name": "Cocos (Keeling) Islands",
"dial_code": "+61",
"code": "CC"
},
{
"name": "Colombia",
"dial_code": "+57",
"code": "CO"
},
{
"name": "Comoros",
"dial_code": "+269",
"code": "KM"
},
{
"name": "Congo",
"dial_code": "+242",
"code": "CG"
},
{
"name": "Congo, The Democratic Republic of the Congo",
"dial_code": "+243",
"code": "CD"
},
{
"name": "Cook Islands",
"dial_code": "+682",
"code": "CK"
},
{
"name": "Costa Rica",
"dial_code": "+506",
"code": "CR"
},
{
"name": "Cote d'Ivoire",
"dial_code": "+225",
"code": "CI"
},
{
"name": "Croatia",
"dial_code": "+385",
"code": "HR"
},
{
"name": "Cuba",
"dial_code": "+53",
"code": "CU"
},
{
"name": "Cyprus",
"dial_code": "+357",
"code": "CY"
},
{
"name": "Czech Republic",
"dial_code": "+420",
"code": "CZ"
},
{
"name": "Denmark",
"dial_code": "+45",
"code": "DK"
},
{
"name": "Djibouti",
"dial_code": "+253",
"code": "DJ"
},
{
"name": "Dominica",
"dial_code": "+1767",
"code": "DM"
},
{
"name": "Dominican Republic",
"dial_code": "+1849",
"code": "DO"
},
{
"name": "Ecuador",
"dial_code": "+593",
"code": "EC"
},
{
"name": "Egypt",
"dial_code": "+20",
"code": "EG"
},
{
"name": "El Salvador",
"dial_code": "+503",
"code": "SV"
},
{
"name": "Equatorial Guinea",
"dial_code": "+240",
"code": "GQ"
},
{
"name": "Eritrea",
"dial_code": "+291",
"code": "ER"
},
{
"name": "Estonia",
"dial_code": "+372",
"code": "EE"
},
{
"name": "Ethiopia",
"dial_code": "+251",
"code": "ET"
},
{
"name": "Falkland Islands (Malvinas)",
"dial_code": "+500",
"code": "FK"
},
{
"name": "Faroe Islands",
"dial_code": "+298",
"code": "FO"
},
{
"name": "Fiji",
"dial_code": "+679",
"code": "FJ"
},
{
"name": "Finland",
"dial_code": "+358",
"code": "FI"
},
{
"name": "France",
"dial_code": "+33",
"code": "FR"
},
{
"name": "French Guiana",
"dial_code": "+594",
"code": "GF"
},
{
"name": "French Polynesia",
"dial_code": "+689",
"code": "PF"
},
{
"name": "Gabon",
"dial_code": "+241",
"code": "GA"
},
{
"name": "Gambia",
"dial_code": "+220",
"code": "GM"
},
{
"name": "Georgia",
"dial_code": "+995",
"code": "GE"
},
{
"name": "Germany",
"dial_code": "+49",
"code": "DE"
},
{
"name": "Ghana",
"dial_code": "+233",
"code": "GH"
},
{
"name": "Gibraltar",
"dial_code": "+350",
"code": "GI"
},
{
"name": "Greece",
"dial_code": "+30",
"code": "GR"
},
{
"name": "Greenland",
"dial_code": "+299",
"code": "GL"
},
{
"name": "Grenada",
"dial_code": "+1473",
"code": "GD"
},
{
"name": "Guadeloupe",
"dial_code": "+590",
"code": "GP"
},
{
"name": "Guam",
"dial_code": "+1671",
"code": "GU"
},
{
"name": "Guatemala",
"dial_code": "+502",
"code": "GT"
},
{
"name": "Guernsey",
"dial_code": "+44",
"code": "GG"
},
{
"name": "Guinea",
"dial_code": "+224",
"code": "GN"
},
{
"name": "Guinea-Bissau",
"dial_code": "+245",
"code": "GW"
},
{
"name": "Guyana",
"dial_code": "+595",
"code": "GY"
},
{
"name": "Haiti",
"dial_code": "+509",
"code": "HT"
},
{
"name": "Holy See (Vatican City State)",
"dial_code": "+379",
"code": "VA"
},
{
"name": "Honduras",
"dial_code": "+504",
"code": "HN"
},
{
"name": "Hong Kong",
"dial_code": "+852",
"code": "HK"
},
{
"name": "Hungary",
"dial_code": "+36",
"code": "HU"
},
{
"name": "Iceland",
"dial_code": "+354",
"code": "IS"
},
{
"name": "India",
"dial_code": "+91",
"code": "IN"
},
{
"name": "Indonesia",
"dial_code": "+62",
"code": "ID"
},
{
"name": "Iran, Islamic Republic of Persian Gulf",
"dial_code": "+98",
"code": "IR"
},
{
"name": "Iraq",
"dial_code": "+964",
"code": "IQ"
},
{
"name": "Ireland",
"dial_code": "+353",
"code": "IE"
},
{
"name": "Isle of Man",
"dial_code": "+44",
"code": "IM"
},
{
"name": "Israel",
"dial_code": "+972",
"code": "IL"
},
{
"name": "Italy",
"dial_code": "+39",
"code": "IT"
},
{
"name": "Jamaica",
"dial_code": "+1876",
"code": "JM"
},
{
"name": "Japan",
"dial_code": "+81",
"code": "JP"
},
{
"name": "Jersey",
"dial_code": "+44",
"code": "JE"
},
{
"name": "Jordan",
"dial_code": "+962",
"code": "JO"
},
{
"name": "Kazakhstan",
"dial_code": "+77",
"code": "KZ"
},
{
"name": "Kenya",
"dial_code": "+254",
"code": "KE"
},
{
"name": "Kiribati",
"dial_code": "+686",
"code": "KI"
},
{
"name": "Korea, Democratic People's Republic of Korea",
"dial_code": "+850",
"code": "KP"
},
{
"name": "Korea, Republic of South Korea",
"dial_code": "+82",
"code": "KR"
},
{
"name": "Kuwait",
"dial_code": "+965",
"code": "KW"
},
{
"name": "Kyrgyzstan",
"dial_code": "+996",
"code": "KG"
},
{
"name": "Laos",
"dial_code": "+856",
"code": "LA"
},
{
"name": "Latvia",
"dial_code": "+371",
"code": "LV"
},
{
"name": "Lebanon",
"dial_code": "+961",
"code": "LB"
},
{
"name": "Lesotho",
"dial_code": "+266",
"code": "LS"
},
{
"name": "Liberia",
"dial_code": "+231",
"code": "LR"
},
{
"name": "Libyan Arab Jamahiriya",
"dial_code": "+218",
"code": "LY"
},
{
"name": "Liechtenstein",
"dial_code": "+423",
"code": "LI"
},
{
"name": "Lithuania",
"dial_code": "+370",
"code": "LT"
},
{
"name": "Luxembourg",
"dial_code": "+352",
"code": "LU"
},
{
"name": "Macao",
"dial_code": "+853",
"code": "MO"
},
{
"name": "Macedonia",
"dial_code": "+389",
"code": "MK"
},
{
"name": "Madagascar",
"dial_code": "+261",
"code": "MG"
},
{
"name": "Malawi",
"dial_code": "+265",
"code": "MW"
},
{
"name": "Malaysia",
"dial_code": "+60",
"code": "MY"
},
{
"name": "Maldives",
"dial_code": "+960",
"code": "MV"
},
{
"name": "Mali",
"dial_code": "+223",
"code": "ML"
},
{
"name": "Malta",
"dial_code": "+356",
"code": "MT"
},
{
"name": "Marshall Islands",
"dial_code": "+692",
"code": "MH"
},
{
"name": "Martinique",
"dial_code": "+596",
"code": "MQ"
},
{
"name": "Mauritania",
"dial_code": "+222",
"code": "MR"
},
{
"name": "Mauritius",
"dial_code": "+230",
"code": "MU"
},
{
"name": "Mayotte",
"dial_code": "+262",
"code": "YT"
},
{
"name": "Mexico",
"dial_code": "+52",
"code": "MX"
},
{
"name": "Micronesia, Federated States of Micronesia",
"dial_code": "+691",
"code": "FM"
},
{
"name": "Moldova",
"dial_code": "+373",
"code": "MD"
},
{
"name": "Monaco",
"dial_code": "+377",
"code": "MC"
},
{
"name": "Mongolia",
"dial_code": "+976",
"code": "MN"
},
{
"name": "Montenegro",
"dial_code": "+382",
"code": "ME"
},
{
"name": "Montserrat",
"dial_code": "+1664",
"code": "MS"
},
{
"name": "Morocco",
"dial_code": "+212",
"code": "MA"
},
{
"name": "Mozambique",
"dial_code": "+258",
"code": "MZ"
},
{
"name": "Myanmar",
"dial_code": "+95",
"code": "MM"
},
{
"name": "Namibia",
"dial_code": "+264",
"code": "NA"
},
{
"name": "Nauru",
"dial_code": "+674",
"code": "NR"
},
{
"name": "Nepal",
"dial_code": "+977",
"code": "NP"
},
{
"name": "Netherlands",
"dial_code": "+31",
"code": "NL"
},
{
"name": "Netherlands Antilles",
"dial_code": "+599",
"code": "AN"
},
{
"name": "New Caledonia",
"dial_code": "+687",
"code": "NC"
},
{
"name": "New Zealand",
"dial_code": "+64",
"code": "NZ"
},
{
"name": "Nicaragua",
"dial_code": "+505",
"code": "NI"
},
{
"name": "Niger",
"dial_code": "+227",
"code": "NE"
},
{
"name": "Nigeria",
"dial_code": "+234",
"code": "NG"
},
{
"name": "Niue",
"dial_code": "+683",
"code": "NU"
},
{
"name": "Norfolk Island",
"dial_code": "+672",
"code": "NF"
},
{
"name": "Northern Mariana Islands",
"dial_code": "+1670",
"code": "MP"
},
{
"name": "Norway",
"dial_code": "+47",
"code": "NO"
},
{
"name": "Oman",
"dial_code": "+968",
"code": "OM"
},
{
"name": "Pakistan",
"dial_code": "+92",
"code": "PK"
},
{
"name": "Palau",
"dial_code": "+680",
"code": "PW"
},
{
"name": "Palestinian Territory, Occupied",
"dial_code": "+970",
"code": "PS"
},
{
"name": "Panama",
"dial_code": "+507",
"code": "PA"
},
{
"name": "Papua New Guinea",
"dial_code": "+675",
"code": "PG"
},
{
"name": "Paraguay",
"dial_code": "+595",
"code": "PY"
},
{
"name": "Peru",
"dial_code": "+51",
"code": "PE"
},
{
"name": "Philippines",
"dial_code": "+63",
"code": "PH"
},
{
"name": "Pitcairn",
"dial_code": "+872",
"code": "PN"
},
{
"name": "Poland",
"dial_code": "+48",
"code": "PL"
},
{
"name": "Portugal",
"dial_code": "+351",
"code": "PT"
},
{
"name": "Puerto Rico",
"dial_code": "+1939",
"code": "PR"
},
{
"name": "Qatar",
"dial_code": "+974",
"code": "QA"
},
{
"name": "Romania",
"dial_code": "+40",
"code": "RO"
},
{
"name": "Russia",
"dial_code": "+7",
"code": "RU"
},
{
"name": "Rwanda",
"dial_code": "+250",
"code": "RW"
},
{
"name": "Reunion",
"dial_code": "+262",
"code": "RE"
},
{
"name": "Saint Barthelemy",
"dial_code": "+590",
"code": "BL"
},
{
"name": "Saint Helena, Ascension and Tristan Da Cunha",
"dial_code": "+290",
"code": "SH"
},
{
"name": "Saint Kitts and Nevis",
"dial_code": "+1869",
"code": "KN"
},
{
"name": "Saint Lucia",
"dial_code": "+1758",
"code": "LC"
},
{
"name": "Saint Martin",
"dial_code": "+590",
"code": "MF"
},
{
"name": "Saint Pierre and Miquelon",
"dial_code": "+508",
"code": "PM"
},
{
"name": "Saint Vincent and the Grenadines",
"dial_code": "+1784",
"code": "VC"
},
{
"name": "Samoa",
"dial_code": "+685",
"code": "WS"
},
{
"name": "San Marino",
"dial_code": "+378",
"code": "SM"
},
{
"name": "Sao Tome and Principe",
"dial_code": "+239",
"code": "ST"
},
{
"name": "Saudi Arabia",
"dial_code": "+966",
"code": "SA"
},
{
"name": "Senegal",
"dial_code": "+221",
"code": "SN"
},
{
"name": "Serbia",
"dial_code": "+381",
"code": "RS"
},
{
"name": "Seychelles",
"dial_code": "+248",
"code": "SC"
},
{
"name": "Sierra Leone",
"dial_code": "+232",
"code": "SL"
},
{
"name": "Singapore",
"dial_code": "+65",
"code": "SG"
},
{
"name": "Slovakia",
"dial_code": "+421",
"code": "SK"
},
{
"name": "Slovenia",
"dial_code": "+386",
"code": "SI"
},
{
"name": "Solomon Islands",
"dial_code": "+677",
"code": "SB"
},
{
"name": "Somalia",
"dial_code": "+252",
"code": "SO"
},
{
"name": "South Africa",
"dial_code": "+27",
"code": "ZA"
},
{
"name": "South Sudan",
"dial_code": "+211",
"code": "SS"
},
{
"name": "South Georgia and the South Sandwich Islands",
"dial_code": "+500",
"code": "GS"
},
{
"name": "Spain",
"dial_code": "+34",
"code": "ES"
},
{
"name": "Sri Lanka",
"dial_code": "+94",
"code": "LK"
},
{
"name": "Sudan",
"dial_code": "+249",
"code": "SD"
},
{
"name": "Suriname",
"dial_code": "+597",
"code": "SR"
},
{
"name": "Svalbard and Jan Mayen",
"dial_code": "+47",
"code": "SJ"
},
{
"name": "Swaziland",
"dial_code": "+268",
"code": "SZ"
},
{
"name": "Sweden",
"dial_code": "+46",
"code": "SE"
},
{
"name": "Switzerland",
"dial_code": "+41",
"code": "CH"
},
{
"name": "Syrian Arab Republic",
"dial_code": "+963",
"code": "SY"
},
{
"name": "Taiwan",
"dial_code": "+886",
"code": "TW"
},
{
"name": "Tajikistan",
"dial_code": "+992",
"code": "TJ"
},
{
"name": "Tanzania, United Republic of Tanzania",
"dial_code": "+255",
"code": "TZ"
},
{
"name": "Thailand",
"dial_code": "+66",
"code": "TH"
},
{
"name": "Timor-Leste",
"dial_code": "+670",
"code": "TL"
},
{
"name": "Togo",
"dial_code": "+228",
"code": "TG"
},
{
"name": "Tokelau",
"dial_code": "+690",
"code": "TK"
},
{
"name": "Tonga",
"dial_code": "+676",
"code": "TO"
},
{
"name": "Trinidad and Tobago",
"dial_code": "+1868",
"code": "TT"
},
{
"name": "Tunisia",
"dial_code": "+216",
"code": "TN"
},
{
"name": "Turkey",
"dial_code": "+90",
"code": "TR"
},
{
"name": "Turkmenistan",
"dial_code": "+993",
"code": "TM"
},
{
"name": "Turks and Caicos Islands",
"dial_code": "+1649",
"code": "TC"
},
{
"name": "Tuvalu",
"dial_code": "+688",
"code": "TV"
},
{
"name": "Uganda",
"dial_code": "+256",
"code": "UG"
},
{
"name": "Ukraine",
"dial_code": "+380",
"code": "UA"
},
{
"name": "United Arab Emirates",
"dial_code": "+971",
"code": "AE"
},
{
"name": "United Kingdom",
"dial_code": "+44",
"code": "GB"
},
{
"name": "United States",
"dial_code": "+1",
"code": "US"
},
{
"name": "Uruguay",
"dial_code": "+598",
"code": "UY"
},
{
"name": "Uzbekistan",
"dial_code": "+998",
"code": "UZ"
},
{
"name": "Vanuatu",
"dial_code": "+678",
"code": "VU"
},
{
"name": "Venezuela, Bolivarian Republic of Venezuela",
"dial_code": "+58",
"code": "VE"
},
{
"name": "Vietnam",
"dial_code": "+84",
"code": "VN"
},
{
"name": "Virgin Islands, British",
"dial_code": "+1284",
"code": "VG"
},
{
"name": "Virgin Islands, U.S.",
"dial_code": "+1340",
"code": "VI"
},
{
"name": "Wallis and Futuna",
"dial_code": "+681",
"code": "WF"
},
{
"name": "Yemen",
"dial_code": "+967",
"code": "YE"
},
{
"name": "Zambia",
"dial_code": "+260",
"code": "ZM"
},
{
"name": "Zimbabwe",
"dial_code": "+263",
"code": "ZW"
}]
"""

FIAT_CURRENCIES = [
            "( AED )  United Arab Emirates Dirham",
            "( AFN )  Afghan Afghani",
            "( ALL )  Albanian Lek",
            "( AMD )  Armenian Dram",
            "( ANG )  Netherlands Antillean Guilder",
            "( AOA )  Angolan Kwanza",
            "( ARS )  Argentine Peso",
            "( AUD )  Australian Dollar",
            "( AWG )  Aruban Florin",
            "( AZN )  Azerbaijani Manat",
            "( BAM )  Bosnia-Herzegovina Convertible Mark",
            "( BBD )  Barbadian Dollar",
            "( BDT )  Bangladeshi Taka",
            "( BGN )  Bulgarian Lev",
            "( BHD )  Bahraini Dinar",
            "( BIF )  Burundian Franc",
            "( BMD )  Bermudan Dollar",
            "( BND )  Brunei Dollar",
            "( BOB )  Bolivian Boliviano",
            "( BRL )  Brazilian Real",
            "( BSD )  Bahamian Dollar",
            "( BTC )  Bitcoin",
            "( BTN )  Bhutanese Ngultrum",
            "( BWP )  Botswanan Pula",
            "( BYN )  Belarusian Ruble",
            "( BZD )  Belize Dollar",
            "( CAD )  Canadian Dollar",
            "( CDF )  Congolese Franc",
            "( CHF )  Swiss Franc",
            "( CLF )  Chilean Unit of Account (UF)",
            "( CLP )  Chilean Peso",
            "( CNH )  Chinese Yuan (Offshore)",
            "( CNY )  Chinese Yuan",
            "( COP )  Colombian Peso",
            "( CRC )  Costa Rican Colón",
            "( CUC )  Cuban Convertible Peso",
            "( CUP )  Cuban Peso",
            "( CVE )  Cape Verdean Escudo",
            "( CZK )  Czech Republic Koruna",
            "( DJF )  Djiboutian Franc",
            "( DKK )  Danish Krone",
            "( DOP )  Dominican Peso",
            "( DZD )  Algerian Dinar",
            "( EGP )  Egyptian Pound",
            "( ERN )  Eritrean Nakfa",
            "( ETB )  Ethiopian Birr",
            "( EUR )  Euro",
            "( FJD )  Fijian Dollar",
            "( FKP )  Falkland Islands Pound",
            "( GBP )  British Pound Sterling",
            "( GEL )  Georgian Lari",
            "( GGP )  Guernsey Pound",
            "( GHS )  Ghanaian Cedi",
            "( GIP )  Gibraltar Pound",
            "( GMD )  Gambian Dalasi",
            "( GNF )  Guinean Franc",
            "( GTQ )  Guatemalan Quetzal",
            "( GYD )  Guyanaese Dollar",
            "( HKD )  Hong Kong Dollar",
            "( HNL )  Honduran Lempira",
            "( HRK )  Croatian Kuna",
            "( HTG )  Haitian Gourde",
            "( HUF )  Hungarian Forint",
            "( IDR )  Indonesian Rupiah",
            "( ILS )  Israeli New Sheqel",
            "( IMP )  Manx pound",
            "( INR )  Indian Rupee",
            "( IQD )  Iraqi Dinar",
            "( IRR )  Iranian Rial",
            "( ISK )  Icelandic Króna",
            "( JEP )  Jersey Pound",
            "( JMD )  Jamaican Dollar",
            "( JOD )  Jordanian Dinar",
            "( JPY )  Japanese Yen",
            "( KES )  Kenyan Shilling",
            "( KGS )  Kyrgystani Som",
            "( KHR )  Cambodian Riel",
            "( KMF )  Comorian Franc",
            "( KPW )  North Korean Won",
            "( KRW )  South Korean Won",
            "( KWD )  Kuwaiti Dinar",
            "( KYD )  Cayman Islands Dollar",
            "( KZT )  Kazakhstani Tenge",
            "( LAK )  Laotian Kip",
            "( LBP )  Lebanese Pound",
            "( LKR )  Sri Lankan Rupee",
            "( LRD )  Liberian Dollar",
            "( LSL )  Lesotho Loti",
            "( LYD )  Libyan Dinar",
            "( MAD )  Moroccan Dirham",
            "( MDL )  Moldovan Leu",
            "( MGA )  Malagasy Ariary",
            "( MKD )  Macedonian Denar",
            "( MMK )  Myanma Kyat",
            "( MNT )  Mongolian Tugrik",
            "( MOP )  Macanese Pataca",
            "( MRU )  Mauritanian Ouguiya",
            "( MUR )  Mauritian Rupee",
            "( MVR )  Maldivian Rufiyaa",
            "( MWK )  Malawian Kwacha",
            "( MXN )  Mexican Peso",
            "( MYR )  Malaysian Ringgit",
            "( MZN )  Mozambican Metical",
            "( NAD )  Namibian Dollar",
            "( NGN )  Nigerian Naira",
            "( NIO )  Nicaraguan Córdoba",
            "( NOK )  Norwegian Krone",
            "( NPR )  Nepalese Rupee",
            "( NZD )  New Zealand Dollar",
            "( OMR )  Omani Rial",
            "( PAB )  Panamanian Balboa",
            "( PEN )  Peruvian Nuevo Sol",
            "( PGK )  Papua New Guinean Kina",
            "( PHP )  Philippine Peso",
            "( PKR )  Pakistani Rupee",
            "( PLN )  Polish Zloty",
            "( PYG )  Paraguayan Guarani",
            "( QAR )  Qatari Rial",
            "( RON )  Romanian Leu",
            "( RSD )  Serbian Dinar",
            "( RUB )  Russian Ruble",
            "( RWF )  Rwandan Franc",
            "( SAR )  Saudi Riyal",
            "( SBD )  Solomon Islands Dollar",
            "( SCR )  Seychellois Rupee",
            "( SDG )  Sudanese Pound",
            "( SEK )  Swedish Krona",
            "( SGD )  Singapore Dollar",
            "( SHP )  Saint Helena Pound",
            "( SLL )  Sierra Leonean Leone",
            "( SOS )  Somali Shilling",
            "( SRD )  Surinamese Dollar",
            "( SSP )  South Sudanese Pound",
            "( STD )  São Tomé and Príncipe Dobra (pre-2018)",
            "( STN )  São Tomé and Príncipe Dobra",
            "( SVC )  Salvadoran Colón",
            "( SYP )  Syrian Pound",
            "( SZL )  Swazi Lilangeni",
            "( THB )  Thai Baht",
            "( TJS )  Tajikistani Somoni",
            "( TMT )  Turkmenistani Manat",
            "( TND )  Tunisian Dinar",
            "( TOP )  Tongan Pa'anga",
            "( TRY )  Turkish Lira",
            "( TTD )  Trinidad and Tobago Dollar",
            "( TWD )  New Taiwan Dollar",
            "( TZS )  Tanzanian Shilling",
            "( UAH )  Ukrainian Hryvnia",
            "( UGX )  Ugandan Shilling",
            "( USD )  United States Dollar",
            "( UYU )  Uruguayan Peso",
            "( UZS )  Uzbekistan Som",
            "( VEF )  Venezuelan Bolívar Fuerte (Old)",
            "( VES )  Venezuelan Bolívar Soberano",
            "( VND )  Vietnamese Dong",
            "( VUV )  Vanuatu Vatu",
            "( WST )  Samoan Tala",
            "( XAF )  CFA Franc BEAC",
            "( XAG )  Silver Ounce",
            "( XAU )  Gold Ounce",
            "( XCD )  East Caribbean Dollar",
            "( XDR )  Special Drawing Rights",
            "( XOF )  CFA Franc BCEAO",
            "( XPD )  Palladium Ounce",
            "( XPF )  CFP Franc",
            "( XPT )  Platinum Ounce",
            "( YER )  Yemeni Rial",
            "( ZAR )  South African Rand",
            "( ZMW )  Zambian Kwacha",
            "( ZWL )  Zimbabwean Dollar"
    ]