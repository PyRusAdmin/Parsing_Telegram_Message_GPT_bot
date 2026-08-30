def preliminary_verification_of_the_link(input_link: str):
    """Проверяет ссылку на валидность"""
    input_link = input_link.strip()
    print(input_link)

    if "@" in input_link:
        clean_link = input_link.replace("@", "")
        print(clean_link)

    if "https://t.me/" in input_link:
        print("Валидная ссылка")


if __name__ == "__main__":
    preliminary_verification_of_the_link("@https://t.me/promokod_skidki_tlt")

    preliminary_verification_of_the_link("@username")
