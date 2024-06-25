def luhn_checksum(card_number: str) -> bool:
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

def validate_card(card_number: str) -> bool:
    # Strip spaces and hyphens
    card_number = card_number.replace(" ", "").replace("-", "")
    
    # Check if the card number consists only of digits
    if not card_number.isdigit():
        return False
    
    # Check length of the card number (typical lengths are between 13 and 19 digits)
    if not 13 <= len(card_number) <= 19:
        return False
    
    # Luhn algorithm check
    return luhn_checksum(card_number)

def get_card_type(card_number: str) -> str:
    card_number = card_number.replace(" ", "").replace("-", "")
    if card_number.startswith("4"):
        return "Visa"
    elif card_number.startswith(("51", "52", "53", "54", "55")):
        return "MasterCard"
    elif card_number.startswith("34") or card_number.startswith("37"):
        return "American Express"
    elif card_number.startswith("6"):
        return "Discover"